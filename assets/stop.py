from PIL import Image

l = []
img_0 = Image.open("/Users/micheleyin/Documents/AI_DBMovie/assets/VR_frame_0.png")
l.append(img_0)
img_1 = Image.open("/Users/micheleyin/Documents/AI_DBMovie/assets/VR_frame_1.png")
l.append(img_1)
for i in range(29):
    l.append(img_0.copy())
    l.append(img_1.copy())

print(len(l))

img_0.save('/Users/micheleyin/Documents/AI_DBMovie/assets/VR_frame.gif', save_all=True, append_images=l, loop=0, fps = 1)