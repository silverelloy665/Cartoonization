from pathlib import Path
import cv2

def main():
    p = Path.cwd() / 'sample_output.mp4'
    print('exists', p.exists())
    cap = cv2.VideoCapture(str(p))
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print('frames', frames)
    ret, frame = cap.read()
    print('read ok', ret)
    if frame is not None:
        print('shape', frame.shape)
    cap.release()

if __name__ == '__main__':
    main()
