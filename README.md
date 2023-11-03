## <p align='center'> Stock-pipeline Project </p>

<br>
<br>
<br>

<div align="center">
  <img src="https://github.com/danielde720/stock-pipeline/assets/141448979/3f1f09dd-0484-44e1-918c-e430b6584afd">
</div>

<br>
<br>


## <p align='center'> Teck Stack: </p>

<table align="center">
  <tr>
    <td align="center">Kafka</td>,
    <td align="center">Cassandra</td>
    <td align="center">Docker</td>
    <td align="center">Airflow</td>
    <td align="center">Streamlit</td>
    <td align="center">Zookeeper</td>
  </tr>
</table>


<br>
<br>


### <p align='center'> Data Source: </p>
- **[Finnhub API](https://finnhub.io/)**: Provides a plethora of real-time data including stock market data, which is the focal point of this project. 


<br>
<br>


### <p align='center'> Data Streaming: </p>
- **Apache Kafka**: Known for its near real-time data processing capabilities, Kafka is used to facilitate data streaming from the Finnhub API to a staging area. In the staging area, the data undergoes a series of data quality and integrity checks before progressing to the `stock_data` topic. Any data failing the checks is rerouted to a monitoring topic named bad_data for further examination. . This mechanism mirrors a production environment where data integrity is paramount, and latency is traded off to ensure data quality. Underneath is a screenshot of our brokers and their configurations using our ui that we defined in our docker compose file.

<br>
<br>

![Screenshot 2023-11-02 at 8 47 19 PM](https://github.com/danielde720/stock-pipeline/assets/141448979/920fd5bf-2283-48f3-8725-8b9a36d1ae06)

<br>
<br>




The architecture of our system is anchored by a cluster composed of three Kafka brokers, which have been containerized using Docker for ease of deployment and scaling. While the data distribution among the brokers is designed to be even, one broker inherently takes on a slightly heavier workload as it serves as the active controller of the cluster. This active controller is pivotal in managing the cluster's metadata and handling administrative tasks. Although only one broker serves as the active controller at any given time, the architecture is resilient to failures as another broker can seamlessly take over the controller role if the active controller fails.

Within the cluster, there are 85 partitions, each having a designated leader responsible for managing the reads and writes for that partition. The distribution of partition leaders across the brokers is balanced to prevent any significant skew. Additionally, the system maintains a robust replica mechanism, with a total of 249 in-sync replicas ensuring data durability and high availability. These in-sync replicas are harmonized with their respective leaders, ready to take over should a leader fail, thereby providing a solid fault-tolerance framework.

The diagram below provides a high-level view of our cluster architecture, illustrating the orchestration between producers, brokers, topics, and consumers, along with the replication mechanism ensuring data integrity and availability.

<br>
<br>

![kafkadrawing](https://github.com/danielde720/stock-pipeline/assets/141448979/40605e42-e5d8-4495-a433-0d414c052293)


<br>
<br>




### <p align='center'> Data Validation: </p> 

<br>
<br>

- **Kafka Staging Area**: A dedicated staging area within Kafka has been established to perform data validation and integrity checks. This is a pivotal step in ensuring that only accurate and complete data is propagated through the pipeline.

- **Monitoring of Unqualified Data**: Instead of leaving unqualified data in the staging area or discarding it, we route it to a designated monitoring topic. This practice enables us to keep a vigilant eye on the quality of data coming from our API. A growing volume of entries in the monitoring topic signals potential issues with the API, allowing us to act promptly to rectify the situation.

- **Quality and Integrity Checks**: The validation process encompasses several checks to maintain data quality and integrity. This includes schema validation, data type verification, and monitoring the frequency of data updates for each symbol. Specifically, we ensure that data for each symbol is updated at least once every four hours to detect any anomalies in data reception.

- **Retention Policy**: While the default retention period is set to 7 days, we've tailored the retention policy to better suit our data processing requirements. The retention period for the staging and `stock_data` topics has been shortened to 3 days to prevent topic overload, while the `bad_data` topic's retention has been extended to 30 days. This extended retention for `bad_data` provides a larger sample to analyze and gauge the frequency of unqualified data received from our API, assisting in maintaining a high-quality data pipeline.

<br>
<br>


### <p align='center'> Database: </p>


<br>
<br>

- **Cassandra NoSQL Database**: The choice of Cassandra as our database technology was motivated by its exceptional capabilities in write optimization and scalability, both vertically and horizontally. Traditional SQL databases are often favored for their strong ACID (Atomicity, Consistency, Isolation, Durability) compliance, ease of querying with a structured query language, and ability to handle complex transactions and joins. However, they can become bottlenecks in high-velocity data ingestion scenarios, especially in distributed environments due to their rigid schema and scaling limitations. On the other hand, NoSQL databases like Cassandra thrive in such scenarios due to their flexible schema, faster writes, and ability to distribute data across many nodes efficiently. While NoSQL databases may present challenges in read efficiency and performing joins, the simplicity of our data schema, which consists of only four columns and does not require joins, mitigates these concerns. Below is a screenshot of data in our table.

<br>
<br>


<p align='center'>
<img src="https://github.com/danielde720/stock-pipeline/assets/141448979/29fa1a27-8226-45c9-97f9-84d81b024fe3)"
</p>


<br>
<br>

  
### <p align='center'> Data Visualization: </p>
- **Streamlit**: A Python-centric tool used to craft an intuitive visualization to represent the stock data interactively. Below is how the visualization looks when it first spins up along with the other containers.

![Screenshot 2023-11-02 at 4 01 47 PM](https://github.com/danielde720/stock-pipeline/assets/141448979/729c4198-73c4-4fa4-b150-a6793f1cad78)


In order to show a graph of how the stock changes over time you have to double click on the symbol and it will show like so.

![Screenshot 2023-11-02 at 4 01 58 PM](https://github.com/danielde720/stock-pipeline/assets/141448979/2685cb12-bdf6-4bab-89c4-4f70ec8e1584)


<br>
<br>


### <p align='center'> Containerization: </p>
- **Docker**: This project embraces Docker for containerization of various components including Kafka brokers (three in total), Cassandra database, Apache Airflow, Streamlit, Zookeeper and other components, all defined in our docker-compose files. Containerization is pivotal for creating an isolated, consistent, and replicable environment for each service, ensuring they run seamlessly across different computing environments. Docker is a key tool in modern backend infrastructure. It's known for making application deployment straightforward and efficient. By wrapping up services in Docker containers, it makes it easy to manage network connections, ensure data consistency across different stages, and handle multiple tasks at once. This project demonstrates how Docker can streamline the setup and scaling of services like Kafka brokers and the Cassandra database, making the system more flexible and easier to manage.


<br>
<br>


### <p align='center'> Data Orchestration: </p>
- **Apache Airflow**: The orchestration of the workflow is managed through Apache Airflow, which ensures a streamlined process from data ingestion, to data quality and integrity checks, and finally, to loading data into Cassandra at scheduled intervals. Initially, there was an option to segregate data and integrity checks into individual tasks, allowing for parallel execution and a chained setup with the core scripts. However, a decision was made to encapsulate all checks within a single script and create distinct staging and production environments. This choice was driven by a desire for a cleaner, less complex setup, and a more controlled data validation and transition phase, emphasizing the importance of data integrity before it reaches the production stage. 
- **Streamlit Integration**: The Streamlit script, is not included in the Airflow DAG. This is because the script is set to run automatically upon spin-up of this project, thereby eliminating the need for orchestration within the DAG. Below is a screenshot of our dag running successfuly.


<br>
<br>


<p align="center">
  <img src="https://github.com/danielde720/stock-pipeline/assets/141448979/bef83c37-c722-45ce-9bf4-de2b521a3970" alt="Screenshot 2023-11-02 at 9 19 16 PM"/>
</p>





