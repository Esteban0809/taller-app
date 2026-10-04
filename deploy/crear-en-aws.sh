#!/bin/bash
# Crea en AWS todo lo necesario para Taller App y lo arranca. Coste aproximado: 12 $/mes.
#   - Rol IAM "taller-app-ec2" para gestionar el servidor con SSM (sin SSH ni claves)
#   - Grupo de seguridad "taller-app-web" con solo los puertos 80 y 443 abiertos
#   - IP elástica (fija) y servidor t4g.micro "taller-app" con 20 GB de disco
# El servidor se instala solo con deploy/servidor-init.sh en su primer arranque.
#
# Uso: bash deploy/crear-en-aws.sh [rama]     (por defecto: feat/despliegue-aws)
set -euo pipefail

REGION=eu-south-2   # España
RAMA="${1:-feat/despliegue-aws}"
NOMBRE=taller-app
TIPO=t4g.micro
TAG="Key=Project,Value=$NOMBRE"
DIR="$(cd "$(dirname "$0")" && pwd)"

if aws ec2 describe-instances --region "$REGION" \
    --filters "Name=tag:Name,Values=$NOMBRE" "Name=instance-state-name,Values=pending,running,stopping,stopped" \
    --query 'Reservations[].Instances[].InstanceId' --output text | grep -q .; then
  echo "Ya existe un servidor '$NOMBRE' en $REGION. No creo otro." >&2
  exit 1
fi

echo "→ Rol IAM para SSM"
if ! aws iam get-role --role-name "$NOMBRE-ec2" >/dev/null 2>&1; then
  aws iam create-role --role-name "$NOMBRE-ec2" --tags "$TAG" \
    --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]}' >/dev/null
  aws iam attach-role-policy --role-name "$NOMBRE-ec2" \
    --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
  aws iam create-instance-profile --instance-profile-name "$NOMBRE-ec2" --tags "$TAG" >/dev/null
  aws iam add-role-to-instance-profile --instance-profile-name "$NOMBRE-ec2" --role-name "$NOMBRE-ec2"
  sleep 10   # el perfil tarda unos segundos en estar disponible para EC2
fi

echo "→ Grupo de seguridad (80 y 443)"
VPC=$(aws ec2 describe-vpcs --region "$REGION" --filters Name=is-default,Values=true --query 'Vpcs[0].VpcId' --output text)
SG=$(aws ec2 describe-security-groups --region "$REGION" --filters "Name=group-name,Values=$NOMBRE-web" "Name=vpc-id,Values=$VPC" \
  --query 'SecurityGroups[0].GroupId' --output text)
if [ "$SG" = "None" ]; then
  SG=$(aws ec2 create-security-group --region "$REGION" --vpc-id "$VPC" --group-name "$NOMBRE-web" \
    --description "Taller App: HTTP y HTTPS publicos" \
    --tag-specifications "ResourceType=security-group,Tags=[{$TAG}]" --query GroupId --output text)
  aws ec2 authorize-security-group-ingress --region "$REGION" --group-id "$SG" --ip-permissions \
    'IpProtocol=tcp,FromPort=80,ToPort=80,IpRanges=[{CidrIp=0.0.0.0/0}]' \
    'IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges=[{CidrIp=0.0.0.0/0}]' >/dev/null
fi

echo "→ IP fija"
read -r ALLOC IP < <(aws ec2 allocate-address --region "$REGION" --domain vpc \
  --tag-specifications "ResourceType=elastic-ip,Tags=[{$TAG},{Key=Name,Value=$NOMBRE}]" \
  --query '[AllocationId,PublicIp]' --output text)

echo "→ Servidor $TIPO (rama $RAMA)"
AMI=$(aws ssm get-parameter --region "$REGION" \
  --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64 --query Parameter.Value --output text)
USER_DATA=$(mktemp)
{ echo '#!/bin/bash'; echo "export RAMA='$RAMA' IP_FIJA='$IP'"; tail -n +2 "$DIR/servidor-init.sh"; } > "$USER_DATA"

INSTANCIA=$(aws ec2 run-instances --region "$REGION" --image-id "$AMI" --instance-type "$TIPO" \
  --security-group-ids "$SG" --iam-instance-profile "Name=$NOMBRE-ec2" \
  --block-device-mappings 'DeviceName=/dev/xvda,Ebs={VolumeSize=20,VolumeType=gp3}' \
  --metadata-options 'HttpTokens=required' \
  --user-data "file://$USER_DATA" \
  --tag-specifications "ResourceType=instance,Tags=[{$TAG},{Key=Name,Value=$NOMBRE}]" \
                       "ResourceType=volume,Tags=[{$TAG},{Key=Name,Value=$NOMBRE}]" \
  --query 'Instances[0].InstanceId' --output text)
rm -f "$USER_DATA"

aws ec2 wait instance-running --region "$REGION" --instance-ids "$INSTANCIA"
aws ec2 associate-address --region "$REGION" --instance-id "$INSTANCIA" --allocation-id "$ALLOC" >/dev/null

URL="https://${IP//./-}.sslip.io"
echo
echo "✓ Servidor $INSTANCIA arrancado con IP $IP"
echo "  Se está instalando solo; tarda unos 5-10 minutos."
echo "  Después tu app estará en: $URL"
