# Robust Networks: An Incentives and Optimization Perspective
Christos Boutsikas, Rohan Garg, Blake Holman, Marios Mertzanidis, Athina Terzoglou, Paritosh Verma


The design of computer networks has become increasingly important as the Internet has become more pervasive. In order to ensure the robustness and high performance of these networks, it is essential to consider the strategic incentives of the individuals and organizations that use them. Furthermore, it is important we analyze the underlying networks themselves and make sure that $(i)$ the network topology evenly distributes the network load between the edges and $(ii)$ that there are no local regions that are more susceptible to congestion. 

In this paper, we systematically analyze existing computer network topologies and routing schemes to empirically and theoretically evaluate their robustness to congestion and strategic behavior. First, we study the role of \textit{expander graphs} and show that their theoretical guarantees provide a way of designing networks that have few connection bottlenecks. 

To understand the robustness of realistic networks, we measure the extent to which they are expanders by simulated them with random graphs. Random Geometric Graphs are commonly used to simulate real-world networks:

<img width="300" alt="Screen Shot 2022-12-07 at 6 13 07 PM" src="https://user-images.githubusercontent.com/7903790/206318850-f9a04f30-fd72-4dfe-9415-31c01742c994.png">                       <img width="300" alt="Screen Shot 2022-12-07 at 6 13 14 PM" src="https://user-images.githubusercontent.com/7903790/206318851-140ca828-8455-43ce-9f5e-7ce61ebd931b.png">

In the end, we opted for the more general Waxman random graph, which has be emperically shown better represent typical networks. We ran experiments to show the extent to which Waxman graphs are good expanders. Lastly, we examined a large network dataset and showed that the network is a 0.01-expander.

We then study the existing network topology of the Internet and compare it to Randomly generated graphs (specifically the Jellyfish topology) to study how they compare to each other in terms of network bottleneck and load distribution. These topologies are 


Here we show our two topologies we tested for congestion: Internet AS Topology and Jellyfish Topology

<img width="300" alt="Screen Shot 2022-12-07 at 6 12 50 PM" src="https://user-images.githubusercontent.com/7903790/206318847-cc8c36ef-9140-4c7a-81bb-889de39f1848.png">                    <img width="300" alt="Screen Shot 2022-12-07 at 6 12 59 PM" src="https://user-images.githubusercontent.com/7903790/206318849-ec6a52e0-c0ee-4589-91db-57d206d3e465.png">

We observe that Jellyfish topology outperforms the network topology of the Internet on various robustness benchmarks and with respect to network construction cost. The plots below show that (i) the jellyfish topology has lesser network bottlenecks, maximum edge load, and the edge load distribution is much more balanced the the Internet AS topology, despite this, (ii) the cost of constructing the jellyfish topology (i.e., network resources it uses) is approximately equal to the cost of constructing the Internet AS topology. Therefore, despite using similar resources, jellyfish topology outperforms the Internet AS topology. Here we show our results for the metrics of Cheeger Constant, Network Resources and, under All-Pairs-Shortest-Paths Routing, Maximum Edge Load and Network Disbalance.


<img width="300" alt="Screen Shot 2022-12-07 at 6 13 28 PM" src="https://user-images.githubusercontent.com/7903790/206318852-5f1c7258-a9b3-4f88-a21f-a111279e6843.png">                    <img width="300" alt="Screen Shot 2022-12-07 at 6 13 35 PM" src="https://user-images.githubusercontent.com/7903790/206318854-d2ddd433-a5ea-465e-ad93-0fc7c4027ac2.png">

<img width="300" alt="Screen Shot 2022-12-07 at 6 13 53 PM" src="https://user-images.githubusercontent.com/7903790/206318855-509a9c17-a416-4d50-a114-ec867d2c1090.png">                    <img width="300" alt="Screen Shot 2022-12-07 at 6 14 03 PM" src="https://user-images.githubusercontent.com/7903790/206318856-b9b4e222-da9f-455e-a64d-7b03f2a29f67.png">


Lastly, we show that when agents and organizations route their information across the network with strategic behavior, both network performance and welfare can suffer. This acts as evidence for the viability of Software Defined Networking (SDNs). Our approach is based on game theory, graph theory, and takes into account both strategic behavior as well as faults that can occur in the network topology. We present simulation results that demonstrate our analysis's effectiveness and discuss our work's potential applications and implications.

<img width="300" alt="Screen Shot 2022-12-07 at 6 50 19 PM" src="https://user-images.githubusercontent.com/7903790/206322139-106d45bd-27c2-4443-a7b9-9ed85ec906f5.png">                    <img width="300" alt="Screen Shot 2022-12-07 at 6 50 30 PM" src="https://user-images.githubusercontent.com/7903790/206322140-b74eeece-8ebd-4389-bd07-286832bf9d3c.png">




