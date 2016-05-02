library(tikzDevice)

## Load a layout developed in Gephi
layout_file = paste(data_folder, 'layout.graphml', sep = '')
graph_layout = read_graph(layout_file, format = 'graphml')
## Copy into the working graph
V(graph)$x = V(graph_layout)$x
V(graph)$y = V(graph_layout)$y
## Discard the separate layout
rm(graph_layout)

## Filter down to giant component
components = components(graph)
graph_gc = induced_subgraph(graph, components$membership == 
						  	which(components$csize == max(components$csize)))

## Cluster using edge betweenness
communities = cluster_edge_betweenness(graph_gc)
## Use betweenness for size
V(graph_gc)$btwn = betweenness(graph_gc, normalized = TRUE)

## Plot the graph
## Output to tikzDevice:
##  NB use vertex.label.cex = .4
#tikz(paste(data_folder, 'graph.tex', sep = ''),standAlone = TRUE)
## Output to high-res PNG
##  NB use vertex.label.cex = 2
png(filename = paste(data_folder, 'graph.png', sep = ''), width = 4000, height = 4000)
plot(graph_gc, 
	 vertex.size = 2 + 30 * V(graph_gc)$btwn, 
	 vertex.color = communities$membership, 
	 #vertex.label = V(graph_gc)$country, 
	 vertex.label = V(graph_gc)$surname,
	 vertex.label.cex = 2,
	 vertex.label.color = 'black',
	 #vertex.label = NA,
	 edge.width = .5, edge.curved = TRUE)
dev.off()
