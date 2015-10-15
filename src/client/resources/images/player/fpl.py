from PIL import Image

Image.open("player.gif").transpose(Image.FLIP_LEFT_RIGHT).save("flipped_player.gif")
