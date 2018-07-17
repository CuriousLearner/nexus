# Server Architecture and configurations

# Third Party Services

Following third-party services are required in order to setup/deploy this project successfully.

## Amazon S3

Amazon Simple Storage Service ([Amazon S3]) is used to store the uploaded media files and static content. It is a scalable and cost-efficient storage solution. 

After [signing up][s3-signup] for Amazon S3, [setup][s3-iam-setup] an IAM user with access to a S3 bucket, you'll need `BUCKET_NAME`, and `AWS_ACCESS_ID` & `AWS_ACCESS_SECRET` of IAM user to setup the project.

[Amazon S3]: http://aws.amazon.com/s3/
[s3-signup]: http://docs.aws.amazon.com/AmazonS3/latest/gsg/SigningUpforS3.html
[s3-iam-setup]: https://rbgeek.wordpress.com/2014/07/18/amazon-iam-user-creation-for-single-s3-bucket-access/

Note: 

- IAM user must have permission to list, update, create objects in S3.

# Deploying Project

The deployment are managed via travis, but for the first time you'll need to set the configuration values on each of the server. Read this only, if you need to deploy for the first time.

### Protecting staging site with Basic Authentication

The project include [django-auth-wall](https://github.com/theskumar/django-auth-wall) which can be used to protect the site with Basic authentication during development. To enable the protection, add the following two variables in system environment or in django settings.

```
AUTH_WALL_USERNAME=<your_basic_auth_username_here>
AUTH_WALL_PASSWORD=<your_basic_auth_password_here>
AUTH_WALL_REALM=<your_basic_auth_message(optional)>
```

### AWS/EC2

For deploying on aws you need to configure all the addons provided and use python-dotenv to store and read enironment variables.

Add the following to your `~/.ssh/config` file.

```
Host nexus.com
    hostname <server_ip_or_>
    user ubuntu
    ForwardAgent yes
    identityfile <PATH_OF_SERVER_PRIVATE_KEY_HERE>
```

Add your github private key to your local ssh-agent, which will be used by ansible on remote server to fetch the code using `ForwardAgent`

    ssh-add <PATH_TO_YOUR_GITHUB_PRIVATE_KEY>

Now you can run the ansible script to setup the machine.

    fab prod configure

This will setup os dependencies, services like supervisor, nginx and fetch our code from Github. Our production environment requires 
some environment variables in `.env`. So you can write a file `prod.env` locally and upload it to server with

    scp prod.env nexus.com:/home/ubuntu/nexus-web/.env

You can also use fab to set environment variables one by one:

    fab prod config:set,<VAR_NAME>,<VAR_VALUE>

Now that you have `.env` setup, you can deploy your code and start services:

    fab prod deploy

