
# SECTION: Total COVID Deaths and Deaths to Cases Ratio

# SUBSECTION: Global Scale

# in order to map global covid data onto a world map, we need uniformity in the
# country names; part of this process had to be done manually by first 
# checking which country names matched between the "world" dataset and the
# jhu covid data set and then manually modifying the ones that did not match
jhu_covid_raw[jhu_covid_raw$Country_Region == "Taiwan*", 
              "Country_Region"] <- "Taiwan"

n_us <- length(jhu_covid_raw[jhu_covid_raw$Country_Region == "US", 
                             "Country_Region"])
jhu_covid_raw[jhu_covid_raw$Country_Region == "US", "Country_Region"] <- 
  rep(c("USA"), times = n_us)

n_uk <- length(jhu_covid_raw[jhu_covid_raw$Country_Region == "United Kingdom", 
                             "Country_Region"])
jhu_covid_raw[jhu_covid_raw$Country_Region == "United Kingdom" ,
              "Country_Region"] <- rep(c("UK"), times = n_uk)

# Koreas
jhu_covid_raw[jhu_covid_raw$Country_Region == "Korea, South", 
              "Country_Region"] <- "South Korea"
jhu_covid_raw[jhu_covid_raw$Country_Region == "Korea, North", 
              "Country_Region"] <- "North Korea"

# Congos
jhu_covid_raw[jhu_covid_raw$Country_Region == "Congo (Kinshasa)", 
              "Country_Region"] <- "Democratic Republic of the Congo" 
jhu_covid_raw[jhu_covid_raw$Country_Region == "Congo (Brazzaville)", 
              "Country_Region"] <- "Republic of Congo"


# etc.
jhu_covid_raw[jhu_covid_raw$Country_Region == "Burma" , 
              "Country_Region"] <- "Myanmar"

jhu_covid_raw[jhu_covid_raw$Country_Region == "Czechia", 
              "Country_Region"] <- "Czech Republic"

jhu_covid_raw[jhu_covid_raw$Country_Region == "Antigua and Barbuda", 
              "Country_Region"] <- "Antigua" 

jhu_covid_raw[jhu_covid_raw$Country_Region == "Cabo Verde", 
              "Country_Region"] <- "Cape Verde"

jhu_covid_raw[jhu_covid_raw$Country_Region == "Cote d'Ivoire",
              "Country_Region"] <- "Ivory Coast"

jhu_covid_raw[jhu_covid_raw$Country_Region == "Eswatini", 
              "Country_Region"] <- "Swaziland"

jhu_covid_raw[jhu_covid_raw$Country_Region == "Holy See", 
              "Country_Region"] <- "Vatican"

jhu_covid_raw[jhu_covid_raw$Country_Region == "Saint Kitts and Nevis", 
              "Country_Region"] <- "Saint Kitts"


jhu_covid_raw[jhu_covid_raw$Country_Region == 
                "Saint Vincent and the Grenadines", "Country_Region"] <- 
  "Saint Vincent"



jhu_covid_raw[jhu_covid_raw$Country_Region == "Trinidad and Tobago", 
              "Country_Region"] <- "Trinidad"



jhu_covid_raw[jhu_covid_raw$Country_Region == "West Bank and Gaza", 
              "Country_Region"] <- "Palestine"

  
  
  
  
# check which country names match and which don't; 
# store matched country names in "mutual_countries" vector
world_map_countries <- unique(world$region)

jhu_countries <- unique(jhu_covid_raw$Country_Region)

mutual_countries <- intersect(world_map_countries, jhu_countries)

# we will use the "world" dataset as our primary dataset;
# we will transfer values of interest from the jhu dataset
# over to the "world" dataset; here, we prepare
# new columns for the variables of interest;
# cf_ratio is case to fatalities ratio where we
# will have it simply be a derived quantity 
# being total_deaths divided by total_cases
# for each country
world['total_cases'] <- NA
world['total_deaths'] <- NA
world['cf_ratio'] <- NA


# iterate through countries in mutual_countries vector; append jhu data
# to world dataset according to country; in the world dataset, there are 
# multiple instances of each country for longitude and latitude columns
# so jhu data will need to be repeated for each country
for (country in mutual_countries){
  # check and store repeat instances of each country in world dataset
  rep_length <- length(world[world$region == country, ]$region)
  
  # append total cases for each country
  world[world$region == country, ]$total_cases <- 
    rep(sum(jhu_covid_raw[jhu_covid_raw$Country_Region == country, 
    ]$Confirmed), times = rep_length)
  
  # append total deaths for each country
  world[world$region == country, ]$total_deaths <- 
    rep(sum(jhu_covid_raw[jhu_covid_raw$Country_Region == country, ]$Deaths),
        times = rep_length)
  
  # evaluate and append total deaths to cases ratio for each country
  world[world$region == country, ]$cf_ratio <-  
    world[world$region == country, 
    ]$total_deaths / world[world$region == country, ]$total_cases
}

  
  
# make NA values zero so they appear on the map
world[is.na(world$total_cases), "total_cases"] <- 0
world[is.na(world$total_deaths), "total_deaths"] <- 0
world[is.na(world$cf_ratio), "cf_ratio"] <- 0

# plot world map with color mapping based on total deaths
plot_deaths <- ggplot() + 
  geom_polygon(data = world, 
               aes(long, lat, group = group, fill = total_deaths), 
               color = "black", size = 0.1) + 
  scale_fill_distiller(palette = "Reds", direction = 1, 
                       breaks = c(200000, 400000, 600000, 800000, 1000000), 
                       limits = c(0, 1200000), labels = comma) + 
  labs(fill='Confirmed \n   Deaths') + 
  theme(axis.text.x = element_blank(),  
        axis.text.y = element_blank(), axis.ticks = element_blank()) + 
  xlab("") + ylab("") + theme(
    panel.background = element_rect(fill = "lightblue",
                                    colour = "lightblue",
                                    size = 0.5, linetype = "solid"),
    panel.grid.major = element_line(size = 0.5, linetype = 'solid',
                                    colour = "white"),
    panel.grid.minor = element_line(size = 0.25, linetype = 'solid',
                                    colour = "white")
  ) + ggtitle("Cumulative COVID Deaths by Country as of 11-01-22")

plot_deaths

  
  
# extract deaths to cases ratio column from world dataset
# and store in a vector with names according to country
cf_ratios_raw <- world$cf_ratio
names(cf_ratios_raw) <- world$region

# filter out zero values when considering deaths to cases ratios
cf_ratios_1 <- cf_ratios_raw[cf_ratios_raw > 0]

# extract only unique values
cf_ratios <- cf_ratios_1[-which(duplicated(cf_ratios_1))]

# extract top 20 deaths to cases ratio values; filter out north korea
# by starting at index 2 up to 21; store in vector "top_cf_ratios"
n <- 20
top_cf_ratios <- sort(cf_ratios, decreasing = TRUE)[2:(n+1)]


# store values as percentages in a dataframe with a separate country column
top_cf_df <- data.frame(country = names(top_cf_ratios), 
                        cf_ratio = top_cf_ratios*100)

# set up top_Cf_df so that deaths to cases ratios are sorted 
# in descending order
top_cf_df$country <- factor(top_cf_df$country, 
                            levels = top_cf_df$country[order(
                              top_cf_df$cf_ratio, decreasing = FALSE)])

  
  
# generate horizontal bar plot for deaths to cases ratio labeled by country 
# in descending order
ggplot(data = top_cf_df, aes(country, cf_ratio)) + 
  geom_col(aes(fill = cf_ratio), color = "black", show.legend = FALSE) + 
  xlab("Country") + ylab("Case-Fatality Ratio (Percentage)") + 
  ggtitle("Top 20 Countries for Case-Fatality Ratio as of 11-01-22") + 
  coord_flip() + scale_fill_distiller(palette = "Reds", direction = 1)

  
  
# **CODE FOR ANIMATION**
# prepare dataframe for animation with 2 distinct frames "a" and "b" where
# frame "a" has all values at zero
top_cf_df$frame <- "b"

# create separate dataframe for the "begin" state with zero values
begin_state <- top_cf_df
begin_state$cf_ratio <- 0
begin_state$frame <- "a"



# set up begin_state so that countries are sorted 
# in the same manner as top_cf_df
begin_state$country <- factor(begin_state$country, 
                              levels = begin_state$country[
                                order(top_cf_df$cf_ratio, decreasing = FALSE)])

# combine the begin_state and top_cf_df datasets
animation_df <- rbind(begin_state, top_cf_df)

# filter out redundant rownames
rownames(animation_df) <- NULL

# prepare plot to be animated 
anim_cf <- ggplot(data = animation_df, aes(country, cf_ratio)) + 
  geom_col(aes(fill = cf_ratio), color = "black", show.legend = FALSE) + 
  xlab("Country") + ylab("Case-Fatality Ratio (Percentage)") + 
  theme(plot.title = element_text(size=12), axis.text=element_text(size=12), 
        axis.title=element_text(size=14)) +
  ggtitle("Top 20 Countries for Case-Fatality Ratio as of 11-01-22") + 
  coord_flip() + scale_fill_distiller(palette = "Reds", direction = 1) + 
  transition_states(
    frame,
    transition_length = 1,
    state_length = 1,
    wrap = FALSE
  ) + ease_aes('linear')


# store animated plot as an animation object called "anim"
anim <- animate(anim_cf, duration = 3, width = 1400, height = 865, 
                res = 200, renderer = ffmpeg_renderer())

# export the animation object as an mp4 file
anim_save("cf_anim.mp4", animation = anim)

  
# SUBSECTION: Continental US Scale


# load US state map data
map_data_us_states <- map_data("state")

# List of States, regions and other areas to be left out of analysis
del_states <- c("Alaska", "Hawaii", "American Samoa", "Diamond Princess", 
                "Grand Princess", "Guam", "Northern Mariana Islands", 
                "Puerto Rico","Virgin Islands")

# subset us_states_data based on regions not in del_states
continental_states_data <- subset(us_states_data, 
                                  !Province_State %in% del_states)

# Store original region names 
original_state_list <- continental_states_data$Province_State

# uncapitalize first letter of region names; store as a vector
continental_states_data$Province_State <- 
  unlist(lapply(continental_states_data$Province_State, tolower))

# prepare to iterate over lower case state names to find number of
# instance appearances in map_data_us_states for each name
state_list <- continental_states_data$Province_State

# prepare vector to store number of state name instances
state_list_lengths <- c()

# manual counter so iteration can be over state names directly
index <- 1
for (state in state_list){
  # find desired length and store in state_list_lengths vector
  state_list_lengths[index] <- length(map_data_us_states[
    map_data_us_states$region == state, "region"])
  index <- index + 1
}

confirmed_column <- rep(continental_states_data$Confirmed, 
                        times = state_list_lengths)

deaths_column <- rep(continental_states_data$Deaths, 
                     times = state_list_lengths)

cf_ratio_column <- rep(continental_states_data$Case_Fatality_Ratio, 
                       times = state_list_lengths)                 


# prepare columns from map_data_us_states to extract for subset
new_columns <- c( "region", "long", "lat", "group", "order" )

# subset map_data_us_states according to the prepared columns
us_states_df <- map_data_us_states[, new_columns]

# append the other prepared columns
us_states_df["confirmed"] <- confirmed_column

us_states_df["deaths"] <- deaths_column

us_states_df["case_fatalities_ratio"] <- cf_ratio_column                     

  
  
  
  
# plot continental US map with color mapping based on total deaths
plot_deaths <- ggplot(data = us_states_df) + 
  geom_polygon(aes(long, lat, group = group, fill = deaths), size = 0.5, 
               color = "black", show.legend = TRUE) + 
  coord_quickmap() + ggtitle(
    "Cumulative COVID Deaths by State in the Continental US as of 11-01-22") + 
  labs(fill='Confirmed \n   Deaths') + 
  scale_fill_distiller(palette = "Reds", direction = 1, limits = c(0, 100000), 
                       breaks = c(20000, 40000, 60000, 80000), labels = comma) + 
  theme(axis.text.x = element_blank(),  axis.text.y = element_blank(), 
        axis.ticks = element_blank()) + xlab("") + ylab("") + 
  theme(panel.background = element_rect(fill = "lightblue", 
                                        colour = "lightblue", 
                                        size = 0.5, linetype = "solid"), 
        panel.grid.major = element_line(size = 0.5, linetype = 'solid',
                                        colour = "white"), 
        panel.grid.minor = element_line(size = 0.25, linetype = 'solid', 
                                        colour = "white"))


plot_deaths

  
  
# reuse original state names (capital first letter)
cap_states <- original_state_list

# extract cf ratios from us_states_df
cf_ratios <- unique(us_states_df$case_fatalities_ratio)

# store cap_states and cf_ratios in a new dataframe called cf_df
cf_df <- data.frame("States" = cap_states, 
                    "Case to Fatalities Ratio" = cf_ratios)

# rearrange cf_df in descending order according to case to fatalities ratio
reordered_cf_df <- cf_df %>% arrange(desc(Case.to.Fatalities.Ratio))

# extract top 20 states from reordered cf_df
top_cf_df <- reordered_cf_df[1:20, ]

# force ordering on top_cf_df
top_cf_df$States <- factor(top_cf_df$States, 
                           levels = top_cf_df$States[
                             order(top_cf_df$Case.to.Fatalities.Ratio, 
                                   decreasing = FALSE)])

# generate horizontal bar plot for deaths to cases ratio labeled by state
# in descending order
ggplot(data = top_cf_df, aes(States, Case.to.Fatalities.Ratio)) + 
  geom_col(aes(fill = Case.to.Fatalities.Ratio), 
           color = "black", show.legend = FALSE) + 
  ylab("Case-Fatality Ratio (Percentage)") + 
  ggtitle("Top 20 States for Case-Fatality Ratio as of 11-01-22") + 
  coord_flip() + scale_fill_distiller(palette = "Reds", direction = 1)

  
  
  
  
# SECTION: GDP Per Capita vs. Daily COVID Deaths


  
# prepare columns desired for sub-dataframe;
# the locations column contains different countries;
# locations columns also contains other values
# not of interest such as "world"
columns <- c("location", "date", "gdp_per_capita", 
             "new_cases_smoothed_per_million",
             "new_deaths_smoothed_per_million", 
             "continent")

# extract desired columns from raw_covid_data
gdp_data <- raw_covid_data[, columns]

# filter out NA values of gdp_per_capita variable
gdp_data_nonull <- gdp_data[-which(is.na(gdp_data$gdp_per_capita)), ]

# create new column called "gdp_per_capita_lvl"; 
# it happens to be the case here that there 
# is a unique gdp_per_capita_value for each
# country which means that the gdp per capita
# for each country not filtered out is assumed to be constant
# throughout the entire time-frame of our data
gdp_data_nonull[, "gdp_per_capita_lvl"] <- 
  round(gdp_data_nonull$gdp_per_capita)

gdp_data_nonull[, "gdp_per_capita_lvl"] <- 
  as.factor(gdp_data_nonull$gdp_per_capita)

  
  
  
# Filter out NA values of new_cases_smoothed_per_million
semi_final_gdp_data <- gdp_data_nonull[
  -which(is.na(gdp_data_nonull$new_cases_smoothed_per_million)), ]

# Filter out NA values of new_deaths_smoothed_per_million
final_gdp_data <- semi_final_gdp_data[-which(
  is.na(semi_final_gdp_data$new_deaths_smoothed_per_million)), ]

# prepare empty vectors to store average daily deaths
# and average daily cases; also prepare empty vectors
# to store gdp_per_capita, continent, and location
avg_cases <- c()
avg_deaths <- c()
gdp_per_capita <- c()
continent <- c()
location <- c()


# iterate through gdp_per_capita factor levels and append elements
# to pertinent vectors

for (i in 1:length(levels(final_gdp_data$gdp_per_capita_lvl))){
  # append average daily cases to avg_cases vector
  avg_cases[i] <- mean(final_gdp_data[final_gdp_data$gdp_per_capita_lvl 
                                      == levels(
                                        final_gdp_data$gdp_per_capita_lvl)[i], 
                                      "new_cases_smoothed_per_million"])
  
  # append average daily deaths to avg_deaths vector
  avg_deaths[i] <- mean(final_gdp_data[
    final_gdp_data$gdp_per_capita_lvl == levels(
      final_gdp_data$gdp_per_capita_lvl)[i],"new_deaths_smoothed_per_million"])
  
  
  
  # append locations to location vector
  location[i] <- final_gdp_data[final_gdp_data$gdp_per_capita_lvl == 
                                  levels(final_gdp_data$gdp_per_capita_lvl)[i], 
                                "location"][1]
  
  # append continents to continent vector
  continent[i] <- final_gdp_data[final_gdp_data$gdp_per_capita_lvl == 
                                   levels(final_gdp_data$gdp_per_capita_lvl
                                   )[i], "continent"][1]
  
  # append gdp_per_capita to gdp_per_capita vector
  gdp_per_capita[i] <- final_gdp_data[
    final_gdp_data$gdp_per_capita_lvl == 
      levels(final_gdp_data$gdp_per_capita_lvl)[i], "gdp_per_capita"][1]
}


  
  
  
  
  
  
  
  
  
# Generate new dataframe based on average daily deaths 
# and average daily cases; also relabel the gdp_per_capita factor levels as 
# positive integers since each level is unique and ordered
new_gdp_frame_raw <- data.frame(gdp_lvl = 1:length(gdp_per_capita), 
                                location = location, avg_cases = avg_cases, 
                                avg_deaths = avg_deaths, Continent = continent, 
                                gdp_per_capita = gdp_per_capita)

# filter out NA values in avg_cases; this also happens to be sufficient
# in filtering out NA values of other columns
new_gdp_frame <- new_gdp_frame_raw[
  -which(is.na(new_gdp_frame_raw$avg_cases)), ]


# prior analysis demonstrates we have skewed data for varaibles of interest;
# apply log transform to variables of interest
new_gdp_frame$log_gdp_per_capita <- log(new_gdp_frame$gdp_per_capita)
new_gdp_frame$log_avg_cases <- log(new_gdp_frame$avg_cases)
new_gdp_frame$log_avg_deaths <- log(new_gdp_frame$avg_deaths)

# filter out the location value "world" 
new_gdp_frame <- new_gdp_frame[!new_gdp_frame$Continent == "", ]

# generate preliminary plot
ggplot(data = new_gdp_frame) + 
  geom_point(aes(gdp_per_capita, avg_deaths, color = Continent)) + 
  xlab("GDP Per Capita (USD)") + ylab("Average Daily New Deaths per Million") + 
  ggtitle("Average Daily Deaths vs. GDP Per Capita (2020-01-01 to 2022-09-27)") 

  
  
  
# plot log transform of average daily deaths against log transform of
# gdp per capita; include regression line with confidence interval,
# correlation coefficient "R" and p-value "p"
  
gdp_plot_deaths <- ggplot(data = new_gdp_frame) + 
geom_point(aes(log_gdp_per_capita, log_avg_deaths, color = Continent)) +  
geom_smooth(formula = 'y~x', method = "lm", 
            aes(log_gdp_per_capita, log_avg_deaths), 
            color = "red", linetype = 2, size = 0.5) + 
xlab("Log(GDP Per Capita)") + 
ylab("Log(Average Daily New Deaths per Million)") + 
theme(plot.title = element_text(size=12))  +  
ggtitle("Average Daily Deaths vs. GDP Per Capita (2020-01-01 to 2022-09-27)")     

gdp_plot_deaths + stat_cor(aes(log_gdp_per_capita, log_avg_deaths), 
                           method="pearson", p.accuracy = 0.001, 
                           r.accuracy = 0.01)

  
  
# apply facet-wrap to the same plot based on different continents
gdp_facet <- ggplot(data = new_gdp_frame, aes(log_gdp_per_capita, 
                                              log_avg_deaths)) + 
geom_point(aes(color = Continent), show.legend = FALSE) + 
geom_smooth(formula = 'y~x', method = "lm", 
            aes(log_gdp_per_capita, log_avg_deaths), 
            color = "red", linetype = 2, size = 0.5)  + 
stat_cor(aes(log_gdp_per_capita, log_avg_deaths), 
         method="pearson", p.accuracy = 0.001, r.accuracy = 0.01, 
         label.x = 3.63, label.y = -5) + xlab("Log(GDP Per Capita)") + 
ylab("Log(Average Daily New Deaths per Million)") +
ggtitle("Average Daily Deaths vs. GDP Per Capita (2020-01-01 to 2022-09-27)") 

gdp_facet + facet_wrap(vars(Continent))
                        
  
  
# SECTION: COVID Vaccine Trends for USA


# filter booster data to only contain "all_ages" age group
raw_boost_data_f1 <- raw_booster_data[
  raw_booster_data$age_group == "all_ages" | 
    raw_booster_data$age_group == "all_ages", ]

# filter booster data to only contain Moderna and Pfizer vaccine products
boost_data <- raw_boost_data_f1[
  raw_boost_data_f1$vaccine_product == "Moderna" | 
    raw_boost_data_f1$vaccine_product == "Pfizer", ]

# filter out case and death outcomes and store them in seaparate
# dataframes; create new column "week" in each dataframe that
# counts the week since starting week
boost_cases <- boost_data[boost_data$outcome == "case", ]
boost_cases$week <- 1:length(boost_cases$mmwr_week)


boost_deaths <- boost_data[boost_data$outcome == "death", ]
boost_deaths$week <- 1:length(boost_deaths$mmwr_week)

# prepare columns that averages moderna and pfizer data together;
# week count is redundant since it is counting moderna and pfizer
# products as separate weeks so we will account for that too

boost_deaths$week <- NA
boost_deaths$avg_no_booster <- NA
boost_deaths$avg_one_booster <- NA
boost_deaths$avg_two_booster <- NA 

# manual counter so we can use iterator to call sections of 
# the boost_deaths dataframe
i = 1

# iterate over unique values of mmwr_week
for (mmwr in unique(boost_deaths$mmwr_week)){
  # append count as week number 
  # (should be numbered according to mmwr_week count)
  boost_deaths[boost_deaths$mmwr_week == mmwr, "week"] <- i
  
  # append average regular vaccine deaths
  boost_deaths[boost_deaths$mmwr_week == mmwr, "avg_no_booster"] <-
    mean(boost_deaths[boost_deaths$mmwr_week == mmwr, 
    ]$vaccinated_with_outcome)
  
  # append average regular vaccine plus one booster deaths
  boost_deaths[boost_deaths$mmwr_week == mmwr, "avg_one_booster"] <- 
    mean(boost_deaths[boost_deaths$mmwr_week == mmwr, 
    ]$one_boosted_with_outcome)
  
  # append average regular vaccine plus two or more booster deaths
  boost_deaths[boost_deaths$mmwr_week == mmwr, "avg_two_booster"] <- 
    mean(boost_deaths[boost_deaths$mmwr_week == mmwr, 
    ]$two_boosted_with_outcome)
  # increment counter
  i = i + 1
}

  
  
  
  
# prepare color mappings according to vaccination status
cols <- c("Unvaccinated" = "red", "One Booster" = "blue", 
          "Regular Vaccination" = "purple", "Two Boosters+" = "green3")

# plot vaccine trend lines according to vaccination status; 
# only Moderna subset is considered since average deaths
# according to vaccine status is the same for both Moderna and Pfizer
ggplot(data = NULL, aes(x = week)) + 
  geom_line(data = boost_deaths[boost_deaths$vaccine_product == "Moderna", ], 
            aes(y = unvaccinated_with_outcome, color = "Unvaccinated")) +
  geom_point(data = boost_deaths[boost_deaths$vaccine_product == "Moderna", ], 
             aes(y = unvaccinated_with_outcome, color = "Unvaccinated")) +
  
  geom_line(data = boost_deaths[boost_deaths$vaccine_product == "Moderna", ], 
            aes(y = avg_no_booster, color = "Regular Vaccination")) +
  geom_point(data = boost_deaths[boost_deaths$vaccine_product == "Moderna", ], 
             aes(y = avg_no_booster, color = "Regular Vaccination")) +
  
  geom_line(data = boost_deaths[boost_deaths$vaccine_product == "Moderna", ], 
            aes(y = avg_one_booster, color = "One Booster")) +
  geom_point(data = boost_deaths[boost_deaths$vaccine_product == "Moderna", ], 
             aes(y = avg_one_booster, color = "One Booster")) +  
  geom_line(data = boost_deaths[boost_deaths$vaccine_product == "Moderna", ], 
            aes(y = avg_two_booster, color = "Two Boosters+")) +
  geom_point(data = boost_deaths[boost_deaths$vaccine_product == "Moderna", ], 
             aes(y = avg_two_booster, color = "Two Boosters+")) +
  ggtitle("US Weekly Deaths by Vaccination Status up to Week of 08-28-22") + 
  theme(plot.title = element_text(size=12)) + xlab("Weeks since 03-20-22") +
  ylab("Deaths") + scale_color_manual(values=cols) + 
  labs(color='Vaccination Status')

  
  
#  **ANIMATION CODE**
# store plot with animation effect in anim_vac
anim_vac <- ggplot(data = NULL, aes(x = week)) + 
geom_line(data = boost_deaths[boost_deaths$vaccine_product == "Moderna", ], 
          aes(y = unvaccinated_with_outcome, color = "Unvaccinated")) +
geom_point(data = boost_deaths[boost_deaths$vaccine_product == "Moderna", ], 
           aes(y = unvaccinated_with_outcome, color = "Unvaccinated")) +

geom_line(data = boost_deaths[boost_deaths$vaccine_product == "Moderna", ], 
          aes(y = avg_no_booster, color = "Regular Vaccination")) +
geom_point(data = boost_deaths[boost_deaths$vaccine_product == "Moderna", ], 
           aes(y = avg_no_booster, color = "Regular Vaccination")) +

geom_line(data = boost_deaths[boost_deaths$vaccine_product == "Moderna", ], 
          aes(y = avg_one_booster, color = "One Booster")) +
geom_point(data = boost_deaths[boost_deaths$vaccine_product == "Moderna", ], 
           aes(y = avg_one_booster, color = "One Booster")) +

geom_line(data = boost_deaths[boost_deaths$vaccine_product == "Moderna", ], 
          aes(y = avg_two_booster, color = "Two Boosters+")) +
geom_point(data = boost_deaths[boost_deaths$vaccine_product == "Moderna", ], 
           aes(y = avg_two_booster, color = "Two Boosters+")) +
ggtitle("US Weekly Deaths by Vaccination Status up to Week of 08-28-22") + 
theme(plot.title = element_text(size=12)) + xlab("Weeks since 03-20-22") +
ylab("Deaths") + scale_color_manual(values=cols) + 
labs(color='Vaccination Status') + transition_reveal(week)

# generate animation object using anim_vac
anim <- animate(anim_vac, width = 1400, height = 865, res = 200, 
                renderer = ffmpeg_renderer())
# save animation object as mp4 file
anim_save("vac_chart.mp4", animation = anim)            
