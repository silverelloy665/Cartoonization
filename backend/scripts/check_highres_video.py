from pathlib import Path
import sys
import cv2


def main(filename: str):
    p = Path(filename)
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
    if len(sys.argv) < 2:
        print('Usage: check_highres_video.py <filename>')
        sys.exit(2)
    main(sys.argv[1])
