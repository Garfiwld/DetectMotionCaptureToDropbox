from imutils.video import VideoStream
import datetime
import imutils
import time
import cv2
import dropbox
import os

lastUploaded = datetime.datetime.now()
motionCounter = 0

client = dropbox.Dropbox("Token")
print("[SUCCESS] dropbox account linked")


vs = VideoStream(src=0).start()
time.sleep(2)

firstFrame = None

while True:
	frame = vs.read()
	timestamp = datetime.datetime.now()
	status = "Unoccupied"

	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	if firstFrame is None:
		firstFrame = gray
		continue

	frameDelta = cv2.absdiff(firstFrame, gray)
	thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)

	for c in cnts:
		if cv2.contourArea(c) < 5000:
			continue
		status = "Occupied"

	ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
	cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
		0.35, (255, 0, 0), 1)
	
	if status == "Occupied":
		if (timestamp - lastUploaded).seconds >= 3.0:
			motionCounter += 1
			if motionCounter >= 8:
				filePath = "./Image/{name}.jpg".format(name=ts)
				cv2.imwrite(filePath , frame)

				print("[UPLOAD] {}".format(ts))
				path = "/{base_path}/{timestamp}.jpg".format(
					base_path="Images", timestamp=ts)
				client.files_upload(open(filePath, "rb").read(), path)
				os.remove(filePath)

				lastUploaded = timestamp
				motionCounter = 0

	else:
		motionCounter = 0
		
	cv2.imshow("Security Feed", frame)
	cv2.imshow("Thresh", thresh)
	cv2.imshow("Frame Delta", frameDelta)
	key = cv2.waitKey(1) & 0xFF

	if key == ord("q"):
		break

cv2.destroyAllWindows()