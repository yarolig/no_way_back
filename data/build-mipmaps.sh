for j in grass.png dirt.png sand.png hills.png; do
    for i in 128 64 32 16 8 4 2 1; do
        echo mkdir -p ${j/.png/.d}
        echo convert $j -resize $i"x"$i ${j/.png/.d}/$i.png
    done
done

