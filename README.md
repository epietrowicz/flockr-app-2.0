# Flockr 2.0 - Now on Tachyon!
Flockr uses a [Tensor Flow Lite model](https://www.kaggle.com/models/google/aiy/tfLite/vision-classifier-birds-v1/3?tfhub-redirect=true) to classify the species of a bird. It was heavily inspired by the [Who's at My Feeder](https://github.com/mmcc-xx/WhosAtMyFeeder/tree/master) project. 

But, in this build, the classificaiton runs locally on a Tachyon which hosts a webpage using a [Cloudflare tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/)

![Video demo](https://youtu.be/Vv7dOztMOqo)

WiFi access is not necessary for this system to work as the traffic is routed over the Tachyon's 5G connection. 

If you want to use the demo route in the web viewer, you will need to add a `test-video.mp4` file to the root of the project's directory. I've [provided a test video](https://drive.google.com/file/d/1tTz1Gps4WgYqqTi08huPQqQcx8DzA_3P/view?usp=sharing), but I cannot promise it will be hosted at this link indefinitely. I encourage sourcing your own.

## Running Fockr
[Docker and Docker Compose](https://docs.docker.com/engine/install/raspberry-pi-os/) are necessary to build and run the container. You'll also need to [have created a Cloudflare tunnel](https://www.youtube.com/watch?v=ey4u7OUAF3c&pp=ygUQY2xvdWRmbGFyZSB1bm5lbA%3D%3D). Once completed, add the Cloudflare token to `docker-compose.yml`.

Make sure that the USB camera is plugged in **before** starting up the containers.

To build: `docker compose up --build`

To run the container: `docker compose up`
