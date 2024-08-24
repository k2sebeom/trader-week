#!/bin/bash
set -e

# Variables
IMAGE_NAME="trader-week"
TAR_FILE="trader_image.tar"
CONTAINER_NAME="trader-week"
REMOTE_TARGET=$1

# Step 1: Build the Docker image
echo "Building Docker image..."
docker build --platform linux/amd64 -t $IMAGE_NAME .

# Step 2: Save the Docker image to a tar file
echo "Exporting Docker image to $TAR_FILE.gz..."
docker save $IMAGE_NAME | gzip > $TAR_FILE.gz

# Step 3: Securely copy the tar file to the remote server using scp
echo "Copying Docker image to remote server..."
scp $TAR_FILE.gz $REMOTE_TARGET:.
scp -r configs $REMOTE_TARGET:.

# Step 4: Clean up
echo "Cleaning up local tar file..."
rm $TAR_FILE.gz

echo "SSH into remote server..."
ssh $REMOTE_TARGET << EOF
    gzip -d $TAR_FILE.gz

    docker stop $CONTAINER_NAME
    docker rmi $IMAGE_NAME

    docker load -i $TAR_FILE
    rm $TAR_FILE

    mkdir -p thumbnails

    docker run -p 3000:3000 \
        -v ./configs:/app/configs \
        -v ./thumbnails:/app/thumbnails \
        --rm -d --name $CONTAINER_NAME \
        $IMAGE_NAME
    docker ps
EOF

echo "Deployment complete!"