-- update data set age = '05-14 years' where age = '5-14 years';
-- select distinct age from data order by age asc

-- select country, sum(suicides_no), sum(gdp_per_capita) as total_gdp_by_capital from data group by country order by total_gdp_by_capital desc;
-- select country, sum("suicides_no") as total_suicide_by_country, sum("HDI_for_year") as total_hdi, sum(" gdp_for_year") as total_gdp, sum("gdp_per_capita") as total_gdp_capita from data group by country order by total_suicide_by_country desc;

-- total suicide by generation
-- select sex, sum("suicides_no") as total_suicide from data group by sex order by sex desc;

-- sex, suicide and generation
-- select  generation, sex, sum("suicides_no") as total_suicide from data group by generation, sex order by total_suicide desc;


-- does suicides corelate to year? no, all the time show there is no gap in overall. clear gap in the end
-- select year, sum("suicides_no") as total_suicides from data group by year


-- does suicide correlate to sex? male have much higher suicide than female
-- select sex, sum("suicides_no") as total_suicide from data group by sex

-- does suicide correlate to age and generation? suicide have higher in people above 35
-- select age, generation, sum("suicides_no") as total_suicides from data group by age, generation

-- does suicide correlate to rich coutry and poor country? not yet
-- select country, sum(" gdp_for_year") as total_gdp, sum("gdp_per_capita") as total_capita, sum("suicides_no") as total_suicide from data group by country order by total_gdp desc;

-- does suicide correlate to rich country over time and population?
-- select country from (select country, sum(" gdp_for_year") as total_gdp, sum("gdp_per_capita") as total_capita, sum("suicides_no") as total_suicide from data group by country order by total_gdp desc;) limit 10;
-- select "top 10 riches country", year, population suicides_no, " gdp_for_year", "gdp_per_capita" from data
-- select "top 10 poorest country", year, population suicides_no, " gdp_for_year", "gdp_per_capita" from data

-- how does the generation suicide overtime in rich and poor country?
-- select "top 10 country has biggest population", year, suicides_no, sex, age, genenration from data
-- select "top 10 country has lowest population", year, suicides_no, sex, age, genenration from data


-- does suicide correlate to location of the country? not yet