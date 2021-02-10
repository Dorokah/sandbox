export image_name=image_provider
export image_tag=1.0

docker build ./ -t $image_name:$image_tag

docker run --rm \
  --name $image_name \
  -e APP_NAME="Dor's sandbox" \
  -e VERSION="beta" \
  -e APP_DESCRIPTION="An app for Dot to play with code" \
  -e PORT=8000 \
  -p 8000:8000 \
  $image_name:$image_tag
