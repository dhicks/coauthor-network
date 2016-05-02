library(cowplot)
library(mgcv)

source('load_data.R')

## Calculate distance based on areas
areas = mdf %>% select(-(id:docs)) %>% names
## Binary distance: https://en.wikipedia.org/wiki/Jaccard_index#Similarity_of_asymmetric_binary_attributes
areas_based_dist = dist({mdf %>% select(one_of(areas))}, method = 'binary') %>%
	as.matrix()
dimnames(areas_based_dist) = list(mdf$sid, mdf$sid)
## Melt into dataframe
dist_df = reshape2::melt(areas_based_dist, value.name = 'areas.distance', 
						 as.is = TRUE)

## Calculate distance based on graph
paths_dist = shortest.paths(graph)
dimnames(paths_dist) = list(V(graph)$sid, V(graph)$sid)
## Melt into dataframe and join with the areas-based distance
dist_df = reshape2::melt(paths_dist, value.name = 'path.distance', as.is = TRUE) %>% 
	full_join(dist_df)
## Fit a GAM, and use its predictions to identify missed connections
dist_df$path.dist.pred = 
	gam(path.distance ~ s(areas.distance, bs = 'cs'), 
		data = dist_df)$fitted.values
dist_df = dist_df %>% mutate(missed.connection = path.distance > 3.5 * path.dist.pred)
## Clean up
rm(areas_based_dist, paths_dist)

## Plotting areas vs. path distance, the smooth, and missed connections
ggplot(data = filter(dist_df, Var1 < Var2), 
	   aes(areas.distance, path.distance)) + 
	geom_point(aes(color = missed.connection), alpha = .05) + 
	scale_color_brewer(palette = 'Set1', 
					   guide = FALSE) +
	geom_line(aes(areas.distance, path.dist.pred), alpha = 1, size = 2)

## Extract the missed connections
missed_df = dist_df %>% filter(missed.connection)

who_is = function (sid) {
	sid = as.character(sid)
	mdf[which(mdf$sid == sid), c('sid', 'given', 'surname', 'country')]
}

var1_df = lapply(missed_df[['Var1']], who_is) %>% do.call(rbind, .)
names(var1_df) = c('Var1', 'given.1', 'surname.1', 'country.1')

var2_df = lapply(missed_df[['Var2']], who_is) %>% do.call(rbind, .)
names(var2_df) = c('Var2', 'given.2', 'surname.2', 'country.2')

missed_df = left_join(missed_df, cbind(var1_df, var2_df))
rm(who_is, var1_df, var2_df)


