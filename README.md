# 🥧 BAKeD 

BAKeD (Branch Analysis in Keboola using DataComPy) is a Streamlit application that provides an easy to use UI for comparing data between production and development branches in Keboola. It uses DataComPy to perform detailed comparisons of datasets and presents the results in an easy-to-understand format.

As a data engineer or data team lead, before merging a branch into production, do you find it cumbersome to make sure that the data is correct?  In my experience, it is most common for a code approver to review code diffs, but it can be an awful pain and prone to human error to have to manually go in and look at the actual data differences between dev and prod.  BAKeD seeks to automate some of that discovery to understand what changes are being made.  For example, if you are making a change to a single column, you want to know that the only thing that changes on that table is in fact, the single column.  BAKeD will display what columns have diffs in them.  Or you may want to know if there are a change in the number of rows, BAKeD prints the number of rows in each environment, and will display an example of the new or deleted rows.  

## Features

- 💻 User-friendly interface of [datacompy results](https://capitalone.github.io/datacompy/polars_usage.html#reports)
- 📈 Detailed comparison metrics including:
  - Match statistics
  - Row counts
  - Column analysis
  - Value differences
  - Unique rows in each environment
- 🔄 Interactive branch selection from Keboola
- 📊 Schema and table comparison between production and development

Example of usage:

![BAKeD UI Screenshot](assets/baked%20demo.gif)


Clearer example of how to print results ... select which branch, which table, and the primary key of the column to join on, and the application will print the results.

![BAKeD UI Screenshot](assets/baked%20config%20detail.png)

## Prerequisites

- Keboola project

## Installation

Assuming that you are installing this directly as a Data App within Keboola, you will want to do the following:

In the Data Apps config in Keboola, you can point to baked.py, or copy/paste the code straight into the Data App.

In order for the application to work, it accesses project data via a Read-Only workspace or Snowflake Destination.  You will need to create one of these in your project. 

## Configuration

Assuming you are installing directly into Keboola, within the Secrets section, set up the following secrets for the read-only workspace you will use.  If you are installing elsewhere, set up the [secrets.toml](https://docs.streamlit.io/develop/concepts/connections/secrets-management) file.

```toml
user = "your_username"
password = "your_password"
account = keboola #(if using keboola on us-west-2 ... if in different region, see https://docs.snowflake.com/en/user-guide/admin-account-identifier)
warehouse = "your_warehouse"
database = "your_database"
```

If you happen to be installing outside of Keboola, you will also want to set up in the .env file with the following as per [docs](As per [docs](https://help.keboola.com/components/data-apps/#access-storage-from-data-app)):
```
KBC_TOKEN=<<<master_token>>>
KBC_URL=<<<ie. https://connection.keboola.com>>>
```



## Usage

 - Start with the branch that you want to compare to the production branch
 - Each dropdown must be selected in order for the application to work. 
   - The storage bucket, table, and columns will load based on the branch selected
 - Allow time for the data for each dropdown to load
 - After selecting the join column for the compare, the application will run datacompy compare. 
 - For more information on datacompy compare, refer to the datacompy [website](https://capitalone.github.io/datacompy/).
- The application uses [Polars method](https://capitalone.github.io/datacompy/polars_usage.html) for datacompy compare. Any issues with the results of the report, are likely due to the underlying datacompy library. 

 
## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Authors

- Created by [Cuesta Partners](https://www.cuestapartners.com) team
- Contributions and thanks to Cuesta Hackathon BAKeD team for the initial build:
    - Daniela Giraldo
    - [Estefany Aguilar](https://www.linkedin.com/in/estefany-aguilar-herrera-120121191/)
    - [Eduardo Mateus](https://www.linkedin.com/in/eduardo-d%C3%ADaz-mateus-47a406143/)
    - [Andres Jaramillo](https://www.linkedin.com/in/afjo/)
- Thanks to Fisa ([Martin Fiser](https://www.linkedin.com/in/fisermartin/)) for suggesting improvements and the beers that led to this idea.
- Contact me at [Marcus Wong](https://www.linkedin.com/in/wongmarcus) for any questions or comments.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Uses [DataComPy](https://github.com/capitalone/cloud-custodian/tree/master/tools/c7n_datacompy) for data comparison
- Integrates with [Keboola](https://www.keboola.com/) and [Snowflake](https://www.snowflake.com/) 