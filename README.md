# CS536-Blogpost
The design of computer networks has become increasingly important as the Internet has become more pervasive. In order to ensure the robustness and high performance of these networks, it is essential to consider the strategic incentives of the individuals and organizations that use them. Furthermore, it is important we analyze the underlying networks themselves and make sure that $(i)$ the network topology evenly distributes the network load between the edges and $(ii)$ that there are no local regions that are more susceptible to congestion.

In this paper, we systematically analyze existing computer network topologies and routing schemes to empirically and theoretically evaluate their robustness to congestion and strategic behavior. We study the role of \textit{expander graphs} and show that their theoretical guarantees provide a way of designing networks that have few connection bottlenecks. 








Additionally, we study the existing network topology of the Internet and compare it to Randomly generated graphs (specifically the Jellyfish topology) to study how they compare to each other in terms of network bottleneck and load distribution. We observe that Jellyfish topology outperforms the network topology of the Internet on various robustness benchmarks and with respect to network construction cost.



![Maximum_Edge_Load](https://user-images.githubusercontent.com/7903790/206316531-d0be97f8-193c-4f42-a815-d56aac4ea174.png)




Lastly, we show that when agents and organizations route their information across the network with strategic behavior, both network performance and welfare can suffer. This acts as evidence for the viability of Software Defined Networking (SDNs). Our approach is based on game theory, graph theory, and takes into account both strategic behavior as well as faults that can occur in the network topology. We present simulation results that demonstrate our analysis's effectiveness and discuss our work's potential applications and implications.





