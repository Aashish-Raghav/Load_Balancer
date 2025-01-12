**The Challenge - Building a Load Balancer**

Step1: Basic routing through load balancer  
Step2: Add scheduling algorithm (Round Robin)  
Step3: Add Threading to check healthy servers and route traffic accordingly  
Step4: Add Asynchronous programming in place of multi-threading  
Step5: Add retry Mechanism to avoid slow, internal, intermittent error etc... in server request or response


Step6: Modularize load balancer in different modules

Justification:  
The primary tasks involve handling network I/O, such as *forwarding requests and checking server health* , **asynchronous programming** allows efficient handling of many concurrent connections with **minimal overhead**. Since creating a new thread for each connection in a **multithreaded** approach would increase memory consumption and limit scalability, asynchronous programming is better suited for scenarios involving high I/O-bound concurrency. Additionally, this approach mirrors how real-world load balancers like Nginx handle concurrency, making it a more realistic and modern solution."
