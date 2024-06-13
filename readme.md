# Customizable Load Balancer

This project is a customizable load balancer built in Python that runs on Docker.

## Design Choices

The design of this load balancer is based on the following principles:

1. **Customizable**: The load balancer can be customized to meet the specific needs of your application.
2. **Scalable**: The load balancer can scale horizontally to handle increased traffic loads.

## Features

- **Customizable**: The load balancer can be customized to meet the specific needs of your application. This includes the ability to configure the number of replicas, the type of load balancing algorithm, and the type of traffic routing.
- **Scalable**: The load balancer can scale horizontally to handle increased traffic loads. This means that as the traffic load increases, the load balancer can automatically add more replicas to distribute the load.
- **Dockerized**: The load balancer is built using Docker, which allows for easy deployment and management of the load balancer.
- **High Availability**: The load balancer can be configured to have multiple replicas, which provides high availability and fault tolerance.

## Prerequisites

To use this load balancer, you will need:
- [Docker](https://www.docker.com/)
- [Python 3.10 and higher](https://www.python.org/) (For running the tests)

## Installation

First, clone the repository to your local machine:

```bash
git clone https://github.com/Arnie1x/LoadBalancer.git
```

Then, navigate to the project directory:

```bash
cd CustomizableLoadBalancer
```

### Docker Setup

To install the load balancer, you will need to have Docker installed on your system. Once Docker is installed, you can run the following command to create the container and run it:

docker compose up --build

This will start the load balancer container in the background.

### Python Setup

To run the load balancer tests, you will need to have Python 3.10 and higher installed on your system. Create a virtual environment and install the required packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The load balancer can be run using the following command:

```bash
python3 /load_balancer/app.py
```

Then, run the tests:

```bash
python3 /tests/a_1.py
python3 /tests/a_2.py
python3 /tests/a_3.py
```

## Usage

Once the load balancer is running, you can access it by visiting the following URL:

http://localhost:5000/home or http://127.0.0.1:5000/home

## Application Structure

The load balancer is built using the following structure:

```
consistent_hashing/
├── __init__.py
├── consistent_hash.py

load_balancer/
├── __init__.py
├── app.py
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
└── requirements.txt

tests/
├── a_1.py
├── a_2.py
└── a_3.py

web_server/
├── server.py
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

The `consistent_hashing` directory contains the code for the consistent hashing algorithm, which is used to distribute traffic among the replicas.

The `load_balancer` directory contains the code for the load balancer itself, which is responsible for managing the replicas and distributing traffic among them.

The `tests` directory contains the test cases for the load balancer, which are used to ensure that the load balancer is functioning correctly.

The `web_server` directory contains the code for the web server, which is a container that runs a simple web application. This container is used to test the load balancer and ensure that it is able to handle incoming requests.

## Performance Testing

### A-1: 10000 async requests on N = 3 server containers

Running 10,000 async requests on N = 3 server containers produces the following results:

![a-1](/outputs/a-1.png "Title")

With both A-1 and A-2 tests, it was initially impossible to run 10,000 async requests due to high CPU load which brought about some requests being dropped. However, after optimizing the code by making use of the `requests_futures.sessions` python library, we were able to limit the maximum number of requests allowed to 100 in the test scripts, which made other requests wait and in turn was able to complete all the 10,000 requests.

The Load Balancer is able to distribute the requests evenly among the replicas, ensuring that the application remains responsive and performs well.

### A-2: 10000 async requests on N = 6 server containers

Running 10,000 async requests on N = 6 server containers produces the following results:

![a-2](/outputs/a-2.png "Title")


With this second test, we were able to run 10,000 async requests on N = 6 server containers, which is a significant increase from the previous test. The Load Balancer was able to distribute the requests although unevenly among the replicas. The application still managed to handle the requests and perform well.

### A-3: Endpoint Testing and Server Failure

Testing the endpoints has been done via scripts with `a_3.py` but mostly using Postman for communicating with all the endpoints.

**/rep** - This endpoint only returns the status of the replicas managed by the load balancer.

![a-3](/outputs/a-3-rep.png "Title")

**/add** - This endpoint adds a new replica to the load balancer.

![a-3](/outputs/a-3-add.png "Title")

**/rm** - This endpoint removes a replica from the load balancer.

![a-3](/outputs/a-3-rm.png "Title")

**Server Failure** - This endpoint simulates a server failure by removing a replica from the load balancer by running `a_3.py`. The load balancer is able to handle the failure by spawning a new replica and distributing the requests evenly among the remaining replicas.

![a-3](/outputs/a-3-server-failure.png "Title")

## Conclusion

In conclusion, the customizable load balancer built using Python and Docker is a powerful tool for distributing traffic among replicas. The load balancer is able to handle high traffic loads and distribute the requests evenly among the replicas, ensuring that the application remains responsive and performs well. The performance testing results show that the load balancer is able to handle a high number of async requests on N = 3 and N = 6 server containers, which is a significant increase from the previous test. The Load Balancer is a valuable tool for any application that requires high availability and scalability.