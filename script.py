import subprocess
import logging
from clearml import Task
import boto3
import os
import base64

def run_docker(command):
    try:
        # Log the command being run
        logging.info(f'Running command: {" ".join(command)}')
        task.get_logger().report_text(f'Running command: {" ".join(command)}')

        # Run the Docker command
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Log the output and errors
        logging.info(f'Output: {result.stdout}')
        task.get_logger().report_text(f'Output: {result.stdout}')
        
        if result.stderr:
            logging.error(f'Error: {result.stderr}')
            task.get_logger().report_text(f'Error: {result.stderr}')

        # Check if the command was successful
        if result.returncode != 0:
            logging.error(f'Command failed with return code: {result.returncode}')
            task.get_logger().report_text(f'Command failed with return code: {result.returncode}')

    except Exception as e:
        logging.error(f'An error occurred: {str(e)}')
        task.get_logger().report_text(f'An error occurred: {str(e)}')

def get_ecr_login_info(region):
    # Create a boto3 client for ECR
    ecr_client = boto3.client('ecr', region_name=region)

    # Get the authentication token
    response = ecr_client.get_authorization_token()
    
    # Extract the authorization token from the response
    auth_data = response['authorizationData'][0]
    token = auth_data['authorizationToken']
    endpoint = auth_data['proxyEndpoint']
    
    # Decode the token
    decoded_token = base64.b64decode(token).decode('utf-8')
    username, password = decoded_token.split(':')

    return username, password, endpoint

def docker_login(username, password, endpoint):
    # Docker login command
    login_command = [
        'docker', 'login',
        '-u', username,
        '-p', password,
        endpoint
    ]

    # Execute the command
    subprocess.run(login_command, check=True)

def pull_docker_image(image_uri):
    # Docker pull command
    pull_command = [
        'docker', 'pull', image_uri
    ]

    # Execute the command
    subprocess.run(pull_command, check=True)

if __name__ == "__main__":
    region = 'ap-south-1'  # Change to your region
    image_uri = '975049994612.dkr.ecr.ap-south-1.amazonaws.com/mnist:latest'  # Change to your image URI

    try:
        # Step 1: Get ECR login information
        username, password, endpoint = get_ecr_login_info(region)

        # Step 2: Log in to Docker
        docker_login(username, password, endpoint)

        # Step 3: Pull the Docker image
        pull_docker_image(image_uri)

        # Step 4: Define your Docker run command here
        docker_command = ['docker', 'run', '-it', '975049994612.dkr.ecr.ap-south-1.amazonaws.com/mnist:latest']
        run_docker(docker_command)

        print("Docker image pulled and run command executed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the ClearML task
        task.close()
