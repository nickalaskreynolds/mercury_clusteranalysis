rm -rf ~/jansky3/plot_orbital/*
cp -r ~/local/nate-research/clusterAnalysis/toyModel_3Body/plot_orbital/*.png ~/jansky3/plot_orbital/
cd ~/jansky3/
sh thumbnail_gifgen.sh
convert -loop 0 -delay 20 ~/jansky3/plot_orbital/chunk_*.gif ~/jansky3/plot_orbital/thumbnail.gif
mv -f ~/jansky3/plot_orbital/thumbnail.gif ~/local/nate-research/clusterAnalysis/toyModel_3Body/plot_orbital/