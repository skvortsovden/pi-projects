import imageio
from operations import list_files

def generate_gif(directory):
    with imageio.get_writer('animation.gif', mode='I', duration=0.2) as writer:
        filenames = list_files(directory)
        for filename in filenames:
            image = imageio.imread(filename)
            writer.append_data(image)