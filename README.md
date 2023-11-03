## <p align='center'> Stock-pipeline Project </p>

<br>
<br>
<br>

<div align="center">
  <img src="https://github.com/danielde720/stock-pipeline/assets/141448979/3f1f09dd-0484-44e1-918c-e430b6584afd">
</div>

<br>
<br>

## <p align='center'> Overview </p>
For this project we are using stock api you can get from here https://finnhub.io/, this api provides near real time data for many things like news,bitcoin, markets ext but for this project we used their near real time stock data as our source to develop a distributed system.The data is then streamed into a Cassandra NoSQL database and we will dockerize it,we chose this as our database due to its abiltiy to scale verticaly and horizonatly  and its optomized for writes , the probelm with nosql databases is that its not efficent for reads and when joins are needed its very unefficent due to its key value architecture, however since their is only 4 columns and joins wont be necesarry at all for our reads this is option has alot of upside with very little downside. We chose Apache Kafka for handling the data streaming because of its near real time data processing is one of the best options out their, we use it send data from the api to a staging area, once in the staging area we run data validation and integrity checks and once passed they get sent to our stock_data topic and the ones that dont pass get sent to another monitoring area for further evalutaion and monitioring.we chose topics to mimic a staging and production enviorment due to its near real time adbilities and since we're trading latency for data integrity via our validation checks we need to minimize our latency and throguput as much as possible. we also containerized our kafka brokers, 3 to be excact to improve network throughput and replication and allows for parallelism distrubtes the workload evenly acroos brokers making it scalable. We then create a pretty cool visualtion using streamlit which provides a pythonic way of creating visualtions. we use  Apache Airflow to orchestrates everything from data ingestion job, to performing our data quality and data integrity checks, to loading data into our cassandra, at scheduled intervals 



## <p align='center'> Project Overview </p>

This project explores a distributed system designed to harness near real-time stock data provided by [Finnhub](https://finnhub.io/). The stock data harvested from the API is then channeled into a Cassandra NoSQL database which will be encapsulated within a Docker container for enhanced scalability and easy deployment.

Here’s a walkthrough of the project's architecture and the rationale behind the tech stack employed:

### Data Source:
- **[Finnhub API](https://finnhub.io/)**: Provides a plethora of real-time data including stock market data, which is the focal point of this project. 

### Data Streaming:
- **Apache Kafka**: Renowned for its near real-time data processing capabilities, Kafka is used to facilitate data streaming from the Finnhub API to a staging area. In the staging area, the data undergoes a series of validation and integrity checks before progressing to the `stock_data` topic. Any data failing the checks is rerouted to a monitoring area for further examination. This mechanism mirrors a production environment where data integrity is paramount, and latency is traded off to ensure data quality.

### Data Validation:
- **Staging Area in Kafka**: A dedicated staging area within Kafka to run data validation and integrity checks. This step is crucial to ensure that only accurate and complete data progresses through the pipeline.

### Database:
- **Cassandra NoSQL Database**: Chosen for its superior write optimization, scalability, both vertically and horizontally. While NoSQL databases can be less efficient for reads and joins due to their key-value architecture, the simplicity of our data schema (comprising of four columns) alleviates this concern, making Cassandra a fitting choice.

### Containerization:
- **Docker**: The project employs Docker to containerize the Kafka brokers (three in total) and the Cassandra database. This setup promotes network throughput, replication, and parallelism, distributing the workload evenly across brokers and making the system scalable.

### Data Orchestration:
- **Apache Airflow**: Orchestrates the entire workflow from data ingestion, data quality, and integrity checks, to loading data into Cassandra, all at scheduled intervals.

### Data Visualization:
- **Streamlit**: A Python-centric tool used to craft an intuitive visualization to represent the stock data interactively.

### Key Advantages:
- The project demonstrates a well-thought-out data pipeline that minimizes latency and maximizes throughput while ensuring data integrity.
- The use of containerization and a distributed database showcases a system built for scalability and reliability, critical attributes for handling real-time financial data.

This project serves as a template for handling real-time data efficiently, ensuring data quality, and presenting the data in a user-friendly, interactive format.
