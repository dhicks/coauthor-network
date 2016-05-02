source('load_data.R')

## Extract the edgelist from the coauthor net, 
##  convert the labels into countries, 
##  and turn into a graph
country_edgelist = as_edgelist(graph) %>%
	apply(., MARGIN = 2, 
		  FUN = function (x) get.vertex.attribute(graph, 'country', index = x))
country_edgelist[is.na(country_edgelist)] = ''
country_edgelist = as.data.frame(country_edgelist)
country_net = graph_from_data_frame(country_edgelist, directed = FALSE)

E(country_net)$weight = 1
country_net = simplify(country_net, edge.attr.comb=list(weight="sum"))
#is_simple(country_net)

## Simplify puts the weights into edges, but we want loop weights in vertices
## So we calculate them manually
n_loops = country_edgelist %>%
	mutate(V1 = as.character(V1), V2 = as.character(V2)) %>%
	filter(V1 == V2) %>% group_by(V1) %>% summarize(n = n())
## Interpolate vertices without loops
n_loops = left_join(data.frame(V1 = V(country_net)$name), n_loops)
## Match to the order of country_net
n_loops = n_loops[match(V(country_net)$name, n_loops$V1),]
## Replace NAs with 0s
n_loops[is.na(n_loops)] = 0
## Write into the graph
V(country_net)$n_loops = n_loops$n
#as_data_frame(country_net, what = 'vertices')

## Divide into clusters
communities = cluster_walktrap(country_net)
communities(communities)

V(country_net)$cluster = membership(communities)

## Uncomment to save
#write_graph(country_net, 'country_net.graphml', format = 'graphml')

## Arrange in a circle and plot
layout_country = layout_in_circle(country_net, 
								  #order = order(V(country_net)$name))
								  order = order(membership(communities)))
## Uncomment the next line and last line to save to file
#png(filename = 'country_net.png', width = 2000, height = 2000)
par(bg = 'grey80')
plot(country_net, layout = layout_country, 
	 vertex.size = .1*V(country_net)$n_loops, 
	 vertex.label.color = communities$membership,
	 vertex.label.cex = 2,
	 vertex.color = 'grey30', 
	 edge.curved = TRUE,
	 edge.color = 'grey30',
	 edge.width = .5*E(country_net)$weight, 
	 palette = RColorBrewer::brewer.pal(length(communities), 'Set1'))
#dev.off()