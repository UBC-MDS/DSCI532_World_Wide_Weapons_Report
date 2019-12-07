# Reflection

## Effective Components of the dashboard:
-	Our two research questions focused on different areas: total of imports/exports in USD, in addition to the relationship of imports/exports as a percentage of GDP. By being able to view both time-series and cross-functional data within the same screen, we were successfully able to capture both research questions, and a user has to scroll minimally to get the takeaways.
-	The ability to look at time-series data for an individual country enables users to see imports/exports around internal and external conflicts.
- The default of the map in the dashboard is to include the US in the map, however since it is such a large importer and exporter, it dominates the scale very heavily. The choice to add a button to either include or remove the US allows the user to see other countries much more clearly - when the US is distinguished as an outlier, the rest of the data is much easier to understand.


## Areas of Improvement/Enhancement for the dashboard:
-	The arms dataset that was chosen was incomplete, and in the earlier years of data available, there are very few countries in the dataset, in addition to other challenges such as gaps in year data, and there were changes to country borders over 30 years. To mitigate this, we could have chosen to look at a smaller time horizon that had more complete data or restricted the regions that were looked at (ie. looked only at North America rather than globally). 
-	The original intention was to have a “Country” callback included in the app, which would have allowed users to interactively select a country in the map and the time-series data for that country would have shown below. This was not technically feasible given the time frame, and so we opted for a dropdown where users can select the country that they would like to see time-series data for.

## Feedback Recieved Issue #40
A summary of feedback is provided below: 

- Add a brief description of the dashboard at the beginning.
- Add information about the data and where it was sourced from.
- Make it clear what each toggle does, specifically the country drop down. Since the graphs that changed with the country drop down were not visible while changing the drop down, the value of the drop down wasn't clear.
- Add grey countries to so that there are no gaps in the map, even if data for a country is missing.
- Change the value to billions USD so values on the axis and tooltip are not large and easier to interpret.
- Make larger changes to layout with either tabs, or a sidebar so the toggles are better connected to their graphs (bigger changes to layout are lower priority, we will try to address toggle confusion through annotation and if time permits change layout.)

## Changes made based on group discussion and feedback:

- Description of the app, toggles and data added to the app. 
- Grey countries have been added so map is complete and missing data is indicated.
- The colour of the plots has been updated to be consistent throughout the dashboard and a gradient of colour has been added to the *Trade as % of GDP* graph, corresponding to the global.
- A slider line has been added to the lowermost visualizations of an individual country the corresponds to the year slider bar for the other graphs, so the year in reference is easier to visualize. 
- Docstrings have been added to all functions
- General code clean up and organization. 

## Feedback Reflections

- Usability: 
  - Generally the app was used how we intended, but having peers review our app was helpful because it allowed us to realize we needed descriptions of some of the toggles. One of the toggles changed a visualization that was at the bottom and required scrolling, so user's didn't understand it's purpose. Another brief description was added to the 'Remove USA' toggle so users can understand why it was created.  
- Repeated observations and suggestions from all reviewers:
  - Not understanding the country drop down, since they had to scroll to see changes. 
  - Changing the map so countries without data were still visible in grey or some other colour.
  - Adding descriptions of the app and toggles. 
A general theme for the feedback was adding brief annotations to the app to address any user confusion. 

Based on the feedback it was easy and appropriate to add descriptions of the app in general, toggles and the data. We also added the grey countries on the map, so a lack of data was interpretable. Some larger scale suggestions, such as adding tabs for the different visualizations, or changing the layout with all the toggles on one side bar were given. However, based on time we decided the addition of descriptions was an easy way to address the reasons these larger scale changes were suggested. The most valuable part of the feedback process was observing the users work with our app. It allowed us to realize any large flaws with the structure, and which changes we needed to prioritize. Overall the feedback led to improvements in the app and has allowed it to become more user friendly. 

