library(cowplot)
library(knitr)

source('load_data.R')

## Researchers, ordered by betweenness centrality
mdf %>% select(surname, given, affiliation, country, deg, docs, btwn) %>% arrange(desc(btwn)) %>% head(10) %>% kable

## Degree and betweenness centrality
ggplot(data = mdf, aes(x = deg, y = btwn)) +
	geom_point() + stat_smooth(method = 'lm') +
	scale_x_log10(name = 'degree') + 
	scale_y_log10(name = 'centrality')

## Number of documents and betweenness centrality
ggplot(data = mdf, aes(x = docs, y = btwn)) +
	geom_point() + stat_smooth(method = 'lm') +
	scale_x_log10(name = 'publications') +
	scale_y_log10(name = 'centrality')


## Country-level stats
country_df = mdf %>% group_by(country) %>% 
	summarize_each_(vars = c('deg', 'btwn', 'docs'), funs = c('sum', 'mean', 'max'))
country_df = mdf %>% group_by(country) %>% summarize(n_authors = n()) %>% left_join(country_df)

## Countries, by descending count of authors
country_df %>% select(country, n_authors) %>% arrange(desc(n_authors))
## Plot
ggplot(data = country_df, aes(x = reorder(country, n_authors), y = n_authors, fill = country)) + 
	geom_bar(stat = 'identity') +
	xlab('country') + ylab('no. authors') +
	guides(fill = FALSE) +
	coord_flip()


## Countries, by descending total number of papers
country_df %>% select(country, docs_sum, docs_mean) %>% arrange(desc(docs_sum))
## Plot
ggplot(data = country_df, aes(x = reorder(country, n_authors), y = n_authors, fill = country)) + 
	geom_bar(stat = 'identity') +
	xlab('country') + ylab('no. authors') +
	guides(fill = FALSE) +
	coord_flip()


## Countries, by descending sum centrality
country_df %>% select(country, btwn_sum) %>% arrange(desc(btwn_sum)) #%>% View
ggplot(data = filter(country_df, btwn_sum > max(btwn_sum)/100), 
	   aes(x = reorder(country, btwn_sum), y = btwn_sum, fill = country)) +
	geom_bar(stat = 'identity') +
	xlab('country') + 
	ylab('aggregate centrality') +
	guides(fill = FALSE) +
	coord_flip()

## Countries, by descending mean centrality
country_df %>% select(country, btwn_mean) %>% arrange(desc(btwn_mean)) #%>% View
# ggplot(data = filter(country_df, btwn_mean > max(btwn_mean)/100), 
# 	   aes(x = reorder(country, btwn_mean), y = btwn_mean)) +
# 	geom_bar(stat = 'identity') +
# 	xlab('country') + 
# 	ylab('mean centrality') +
# 	coord_flip()

btwn_plot_countries = country_df %>% filter(btwn_mean > 0) %>% .[['country']]
## Barplot of means, with jittered individual values
ggplot(data = filter(country_df, country %in% btwn_plot_countries),
					 aes(x = reorder(country, btwn_mean), 
							  y = btwn_mean, color = country, fill = country)) +
	geom_bar(stat = 'identity', width = .05) +
	geom_point(data = filter(mdf, country %in% btwn_plot_countries), 
			   aes(x = country, y = btwn), position = 'jitter') +
	guides(color = FALSE, fill = FALSE) +
	ylab('centrality (mean)') + #scale_y_log10() +
	xlab('country') +
	coord_flip()

## Individual values
##  NB scale_y_log10 applies the log before calculating the means, 
##    producing errors if we try to use stat_summary
ggplot(data = filter(mdf, country %in% btwn_plot_countries), 
	   aes(x = reorder(country, btwn, FUN = mean), y = btwn, color = country), 
	   position = 'jitter') +
	geom_point() + 
	#stat_summary(fun.y = 'mean', geom = 'point', shape = '|', size = 3) +
	guides(color = FALSE, fill = FALSE) +
	ylab('centrality') + scale_y_log10() +
	xlab('country') +
	coord_flip() 

## Relationship between number of authors and mean centrality
ggplot(data = filter(country_df, btwn_sum > 0), 
	   aes(n_authors, btwn_mean, color = country)) + 
	geom_label(aes(label = country)) +
	stat_smooth() +
	guides(color = FALSE) + scale_x_log10() + scale_y_log10()

