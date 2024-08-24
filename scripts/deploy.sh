#!/bin/bash
set -e

# Variables
IMAGE_NAME="trader-week"
TAR_FILE="docker_image.tar"
REMOTE_USER="ec2-user"
REMOTE_TARGET=$1

# Step 1: Build the Docker image
echo "Building Docker image..."
docker build --platform linux/amd64 -t $IMAGE_NAME .

# Step 2: Save the Docker image to a tar file
echo "Exporting Docker image to $TAR_FILE..."
docker save -o $TAR_FILE $IMAGE_NAME

# Step 3: Securely copy the tar file to the remote server using scp
echo "Copying Docker image to remote server..."
scp $TAR_FILE $REMOTE_TARGET:.

# Step 4: Clean up
echo "Cleaning up local tar file..."
rm $TAR_FILE

echo "Deployment complete!"

# Step 5: SSH to remote host for control
echo "SSH into remote server..."
ssh $REMOTE_TARGET
