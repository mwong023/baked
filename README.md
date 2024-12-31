# 🥧 BAKeD 

BAKeD (Branch Analysis in Keboola using DataComPy) is a Streamlit application that provides an interactive interface for comparing data between production and development branches in Keboola. It uses DataComPy to perform detailed comparisons of datasets and presents the results in an easy-to-understand format.

## Features

- 🔄 Interactive branch selection from Keboola
- 📊 Schema and table comparison between production and development
- 📈 Detailed comparison metrics including:
  - Match statistics
  - Row counts
  - Column analysis
  - Value differences
  - Unique rows in each environment
- 🎯 Visual progress indicators for match rates
- 💻 User-friendly interface built with Streamlit

## Prerequisites

- Python 3.9+
- Snowflake account
- Keboola account with API access
- Required Python packages (see `requirements.txt`)

## Installation

Assuming that you are installing this directly as a Data App within Keboola, you will want to do the following:

In the Data Apps config in Keboola, you can point to baked.py, or copy/paste the code straight into the Data App.

In order for the application to work, it accesses project data via a Read-Only workspace or Snowflake Destination.  You will need to create one of these in your project. 

## Configuration

Assuming you are installing directly into Keboola, within the Secrets section, set up the following secrets for the read-only workspace you will use.  If you are installing elsewhere, set up the [secrets.toml](https://docs.streamlit.io/develop/concepts/connections/secrets-management) file.

```toml
user = "your_username"
password = "your_password"
account = "your_account"
warehouse = "your_warehouse"
database = "your_database"
```

If you happen to be installing outside of Keboola, you will also want to set up a token in the .env file with the following as per [docs](As per [docs](https://help.keboola.com/components/data-apps/#access-storage-from-data-app)):
 - KBC_TOKEN
 - KBC_URL



## Usage

 - Start with the branch that you want to compare to the production branch
 - Each dropdown must be selected in order for the application to work. 
   - The storage bucket, table, and columns will load based on the branch selected
 - Allow time for the data for each dropdown to load
 - After selecting the join column for the compare, the application will run datacompy compare. 
 - For more information on datacompy compare, refer to the datacompy [website](https://capitalone.github.io/datacompy/).
- The application uses [Polars method](https://capitalone.github.io/datacompy/polars_usage.html) for datacompy compare. 
 
## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Authors

- Created by [Cuesta Partners](https://www.cuestapartners.com)
- Contributions and thanks to Cuesta Hackathon BAKeD team for the initial build:
    - Daniela Giraldo
    - [Estefany Aguilar](https://www.linkedin.com/in/estefany-aguilar-herrera-120121191/)
    - [Eduardo Mateus](https://www.linkedin.com/in/eduardo-d%C3%ADaz-mateus-47a406143/)
    - [Andres Jaramillo](https://www.linkedin.com/in/afjo/)
- Thanks to Fisa ([Martin Fiser](https://www.linkedin.com/in/fisermartin/)) for suggesting improvements and the beers that led to this idea.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Uses [DataComPy](https://github.com/capitalone/cloud-custodian/tree/master/tools/c7n_datacompy) for data comparison
- Integrates with [Keboola](https://www.keboola.com/) and [Snowflake](https://www.snowflake.com/) 