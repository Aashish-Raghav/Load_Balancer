# Asynchronous Load Balancer  

## Overview  
This project is a **scalable asynchronous load balancer** designed to efficiently route client requests across multiple backend servers. It is built using Python's `asyncio` and `aiohttp` libraries, supporting advanced routing algorithms and ensuring high availability and reliability through health checks and retry mechanisms.  

## Features  
- **Asynchronous Programming:** Efficient handling of numerous concurrent connections with minimal overhead.  
- **Routing Algorithms:** Implements Weighted Round Robin, Least Connection, and Consistent Hashing for dynamic load distribution.  
- **Health Checks & Retry Mechanisms:** Ensures 99.99% uptime by routing requests only to healthy servers and retrying failed requests.  
- **Real-Time Server Management:** API endpoints for adding or removing servers from the server ring without restarting the load balancer.  
- **Comprehensive Logging:** Enhanced monitoring and debugging for improved reliability and traceability.  

---

## The Challenge - Building a Load Balancer  
The goal was to design a load balancer capable of efficiently managing network I/O, ensuring high concurrency and scalability. The development process was broken down into the following steps:  

### Step 1: Basic Routing  
Implemented basic routing logic to forward client requests to backend servers.  

### Step 2: Scheduling Algorithm (Round Robin)  
Added a **Round Robin** scheduling algorithm to distribute requests evenly across servers.  

### Step 3: Multithreaded Health Checks  
Introduced multithreading for continuous health checks, ensuring requests are routed only to active servers.  

### Step 4: Asynchronous Programming  
Replaced the multithreaded approach with **asyncio**, leveraging coroutines for efficient I/O-bound concurrency. This transition was driven by the need for scalability and minimal memory consumption.  

### Step 5: Retry Mechanism  
Added an **exponential backoff retry mechanism** to handle slow, internal, or intermittent errors during server requests or responses.  

### Step 6: Modularization  
Refactored the codebase into **modular components**, enhancing maintainability and scalability.  

### Step 7: Weighted Round Robin  
Integrated **Weighted Round Robin** scheduling, allowing requests to be distributed based on server capacity.  

### Step 8: Dictionary-Based Server Tracking  
Replaced the array-based healthy server tracking with a **dictionary-based approach**, optimizing lookup and update operations.  

### Step 9: Least Connection Algorithm  
Implemented the **Least Connection** scheduling algorithm to route requests to the server with the fewest active connections.  

### Step 10: Consistent Hashing & Real-Time Server Management  
Added **Consistent Hashing** for better request distribution and fault tolerance.  
Introduced API endpoints to **add or remove servers** in real time, ensuring minimal request disruption.  

---

## Justification  
The primary tasks of this load balancer involve handling network I/O, such as forwarding client requests and performing health checks. Using **asynchronous programming** allows efficient management of multiple concurrent connections with minimal overhead.  

### Why Asynchronous Programming?  
- **High I/O-bound Concurrency:** Unlike multithreading, asynchronous programming avoids the overhead of creating new threads for each connection, improving memory efficiency and scalability.  
- **Real-World Relevance:** This approach mirrors how modern load balancers like **Nginx** handle concurrency, making it a more realistic and industry-relevant solution.  
- **Performance Optimization:** Enables non-blocking operations, allowing the system to remain responsive even under heavy loads.  

---

## Getting Started  

### Prerequisites  
- Python 3.11+  
- `aiohttp` and `asyncio` libraries  

### Installation  
```bash
git clone https://github.com/Aashish-Raghav/Load_Balancer.git
cd Load_balancer
pip install -r requirements.txt
```

## Usage  
To get the load balancer usage, use the following command:  
```bash
python main.py --help
```

---

## Future Enchancement

- **Dynamic Load Balancing:** Adjust routing decisions based on real-time server load metrics to optimize resource utilization.  
- **TLS Termination:** Add HTTPS support for secure communication between clients and the load balancer.  
- **Web Dashboard:** Develop a dashboard to visualize server health, request distribution, and performance metrics.

---
