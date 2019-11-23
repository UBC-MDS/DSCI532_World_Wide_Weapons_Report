# Proposal

### Motivation and Purpose
One of the key topics in the October 2019 Canadian Federal Election was [gun control]( https://toronto.citynews.ca/2019/10/02/how-are-the-federal-parties-tackling-public-safety-and-gun-violence/) and how parties would respond to the shocking increase in gun violence. In the United States, the Second Amendment, or the right to bear arms is baked into the [Bill of Rights]( https://en.wikipedia.org/wiki/Second_Amendment_to_the_United_States_Constitution). These are two examples that have been polarizing to North Americans, but the use of weapons including guns is a worldwide issue, and not only in relation to war and terrorism. It is clear that weapons move around the world, and the technologies available for weapon production varies between countries. What is less clear is where weapons move from and to, and how significant the movement of weapons is in global and national economies. We would like to use our dashboard to explore how import, export, and net import (imports less exports) of weapons is reflected in economies around the world both over time and comparatively. 

### Description of the Data

To populate our dashboard, we will be using the following two datasets:

- [Worldwide Arms and Ammunition Trading](http://data.un.org/Data.aspx?d=ComTrade&f=_l1Code%3a93) dataset by [United Nations Statistics Department](https://unstats.un.org/home/), covering roughly last 30 years (1988 - 2018) of international import/export trading operations of different kinds of arms/ammunition and related goods (per country per year).
Since we are only interested in total import/export by country by year, we will be summarizing all individual weapon kinds import/export USD values into a **Total Value** feature. After some wrangling, we get a tidy dataset with the following features:
    - **Country** - observation country name
    - **Year** - observation year (from 1988 to 2018)
    - **Direction** - trade operation direction (import or export)   
    - **Total Value** - total USD value for the given country on given year for given trade direction summarized across all kinds of weapons / arms / ammunitions
       
- [GDP by Country](https://data.worldbank.org/indicator/NY.GDP.MKTP.CD) dataset by [The World Bank](https://www.worldbank.org/), providing inflation-adjusted Gross Domestic Product for most countries for the period of 1960-2018. The dataset comes untidy, and after some wrangling/melting we can extract the following useful features:
    - **Country** - observation country name
    - **Year** - observation year (from 1960 to 2018)
    - **GDP** - country's GDP value for the observation year (current USD)

To produce some of the visualizations, the datasets will be later inner-joined by the **Country / Year** features of each dataset. 

NOTE: Original datasets are stored in the [data / dirty](data/dirty) folder. Use [scripts/clean-data.py](/scripts/clean-data.py) to transform and clean the data. 
Once cleaned, the tidy datasets are stored in the [data / clean](data/clean) folder.

### Research Questions and Usage Scenarios

Our app will provide answers to two research questions:

1. How have weapons moved around the world in the last 30 years?
2. How does net import of weapons change as a percentage of GDP overtime?

#### Usage Scenario: 
Sarah is a reporter who would like to understand the role that weapons play in a countries GDP overtime, and what factors influence the movement of weapons globally through import and export. Specifically, she would like to [explore] how increases and decreases in conflict around the world effects movement of weapons and [identify] whether this has any effect on the GDP of a country. By being able to look at movement of weapons through time, she can [compare] the year conflicts occurred to changes in import and export for those regions in conflict, as well as other countries. She will be able to filter out specific countries to see how their national trends compare to global changes in weapon movements. Sarah suspects that certain events that lead to conflict, like 911, will affect the movement of weapons globally and that this will effect the GDP of certain countries. However, she also assumes that there are many additional factors that contribute to the movement of weapons globally. 
