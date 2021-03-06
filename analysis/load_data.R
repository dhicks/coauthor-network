library(cowplot)
library(dplyr)
library(igraph)
library(knitr)

## Load metadata CSV file
mdf_file = paste(data_folder, 'combined_metadata.csv', sep = '')
mdf = read.csv(mdf_file, stringsAsFactors = FALSE)

## Coerce area columns to logical
mdf_areas = mdf %>% 
	select(-(X:surname)) %>% 
	sapply(function (x) x == 'True')

## Fix Kosovars
kosovar_affiliations = c('Universiteti i Prishtines', 
						 'Consulate of the Republic of Kosovo')
mdf[mdf$affiliation %in% kosovar_affiliations,]$country = 'Kosovo'

## Fix the country levels
fix_country_levels = function (level) {
	if (level == '') {
		level = NA
	} else if (level == 'yug') {
		level = 'Yugoslavia'
	} else if (level == 'rou') {
		level = 'Romania'
	} else if (grepl('\\[', level)) {
		countries = regmatches(level, gregexpr("'[^']*'", level))[[1]]
		countries = gsub("'", "", countries)
		if (length(countries) == 1) {
			level = countries
		} else if (countries[1] == '') {
			level = countries[2]
		} else if (countries[1] == countries[2]) {
			level = countries[1]
		} else {
			level = 'Multiple'
		}
	} else {
		level = level
	}
	
	level
}
mdf$country = sapply(mdf$country, fix_country_levels)
rm(fix_country_levels)

## Remove some columns we don't need, 
##  fix the formatting of id to match the graphml, and
##  turn affiliation and country into factors
mdf_main = mdf %>% 
	transmute(id = paste('n', X, sep = ''),
			  sid = sid,
			  surname = surname,
			  given = given,
			  affiliation = as.factor(affiliation),
			  country = as.factor(country),
			  docs = docs)
## Combine the main metadata w/ the area columns
mdf = cbind(mdf_main, mdf_areas)
## Discard the interim variables
rm(mdf_areas, mdf_main, mdf_file)

## Load graph
graph_file = paste(data_folder, 'coauth_net.graphml', sep = '')
graph = read_graph(graph_file, format = 'graphml')
## Replace country field with corrected version from mdf
V(graph)$country = as.character(mdf$country)
## Calculate graph statistics
graph_stats = data.frame(id = V(graph)$id, 
						 deg = degree(graph), 
						 btwn = betweenness(graph, normalized = FALSE), 
						 component = components(graph)$membership,
						 stringsAsFactors = FALSE) %>%
	mutate(btwn = btwn / max(btwn))
## Combine with the metadata
mdf = left_join(graph_stats, mdf)
## Discard the interim variables
rm(graph_stats, graph_file)


