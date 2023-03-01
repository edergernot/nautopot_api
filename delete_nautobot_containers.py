import subprocess
subprocess.run( ['docker', 'system', 'prune', '-a', '-f' ] )
images = []
DockerImages = subprocess.getoutput(['docker', 'image', 'ls'])
for line in DockerImages.split('\n'):
    ImageId= line.split()[2]
    if "IMAGE" == ImageId:
        continue
    ID = line.split()[2]
    print(f"Image: {line.split()[0]} is ID: {ID}")
    images.append(ImageId)

for image_id in images:
    subprocess.run(['docker', 'image', 'rm', '-f' , image_id])





