library(knitr)

source('load_data.R')

areas = mdf %>% select(-(id:docs)) %>% names

## ----------
## Cluster analysis
areas_data = mdf %>% select(one_of(areas))
areas_dist = dist(t(areas_data*1), method = 'binary')
areas_hclust = hclust(areas_dist)
#plot(as.dendrogram(areas_hclust), horiz = TRUE)
areas_clusters = cutree(areas_hclust, k = 40)
areas_df = data.frame(area = areas, cluster = areas_clusters)
#table(areas_df$cluster)
areas_df %>% group_by(cluster) %>% 
	summarize(n_areas = n(), areas = paste(area, collapse = '; ')) %>% kable

## ----------
## Coverage of the top 15, 30, and 45 areas
areas_15 = mdf %>% select(one_of(areas)) %>% summarize_each('sum') %>% 
	sort(decreasing = TRUE) %>% names %>% head(n=15)

areas_30 = mdf %>% select(one_of(areas)) %>% summarize_each('sum') %>%
	sort(decreasing = TRUE) %>% names %>% head(n=30)

areas_45 = mdf %>% select(one_of(areas)) %>% summarize_each('sum') %>%
	sort(decreasing = TRUE) %>% names %>% head(n=45)

mdf %>% select(one_of(areas_20)) %>% rowSums() %>% is_greater_than(0) %>% 
	sum %>% divide_by(nrow(mdf))

areas_coverage = function (areas) {
	mdf %>% select(one_of(areas)) %>% rowSums() %>% is_greater_than(0) %>%
		sum %>% divide_by(nrow(mdf))
}

areas_to_string = function (areas) {
	areas %>% paste(collapse = '; ') %>% 
		gsub('\\.\\.', '\\.', .) %>% gsub('\\.', ' ', .)
}

areas_list = list(areas_15 = areas_15, areas_30 = areas_30, areas_45 = areas_45)
areas_coverage_df = data.frame(
						areas = sapply(areas_list, areas_to_string),
						coverage = sapply(areas_list, areas_coverage)
)

areas_coverage_df %>% kable

## ----------
## Country x areas
country_areas = mdf %>% group_by(country) %>% select(one_of(areas)) %>% 
	summarize_each('sum') %>% 
	reshape2::melt(id.vars = 'country') %>% 
	filter(value != 0)

## Heatmap: all countries and areas
ggplot(data = country_areas, 
	   aes(country, variable, fill = value)) + 
	geom_tile() + 
	scale_fill_gradient(low = 'yellow', high = 'red') +
	theme(axis.text.x = element_text(hjust = 1, angle = 45), 
		  axis.text.y = element_text(size = 3))

## Heatmap: countries and top 45 areas
ggplot(data = filter(country_areas, variable %in% areas_45), 
	   aes(country, variable, fill = value)) +
	geom_tile() +
	scale_fill_gradient(low = 'yellow', high = 'red') +
	theme(axis.text.x = element_text(hjust = 1, angle = 45), 
		  axis.text.y = element_text(size = 6))

## Heatmap:  countries and areas with more than a certain number of individuals
ggplot(data = {country_areas %>% filter(value > 10)}, 
	   aes(country, variable, fill = value)) +
	geom_tile() + 
	scale_fill_gradient(low = 'yellow', high = 'red')+
	theme(axis.text.x = element_text(hjust = 1, angle = 45), 
		  axis.text.y = element_text(size = 6))

## Not actually a useful graph
# country_areas_graph = graph_from_data_frame(country_areas, directed = FALSE)
# V(country_areas_graph)$type = bipartite_mapping(country_areas_graph)$type
# layout = layout_with_sugiyama(country_areas_graph,
# 							  hgap = 100, vgap = .5)
# plot(country_areas_graph,
# 	 vertex.label.cex = .5,
# 	 vertex.size = 5, vertex.color = V(country_areas_graph)$type,
# 	 edge.width = E(country_areas_graph)$value,
# 	 layout = layout$layout)
