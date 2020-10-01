#!/usr/bin/env python3

import time

import control
import updater


class PanelControl(control.BoardControlBase):

    def __init__(self, n_banks=2, n_rows=16, n_cols=64, colordepth=16,  **kwargs):
        # Super call
        super().__init__(**kwargs)

        # Save panel description
        self.n_banks = n_banks
        self.n_rows  = n_rows
        self.n_cols  = n_cols
        self.colordepth = colordepth

        # Pre-create buffers
        self.line_bytes = n_cols * (colordepth // 8)
        self.send_buf = bytearray(1 + self.line_bytes)
        self.send_buf_view = memoryview(self.send_buf)

    def send_line_data(self, data):
        self.send_buf_view[0] = 0x80
        self.send_buf_view[1:] = data
        self.slave.exchange(self.send_buf)

    def send_frame_data(self, frame):
        # View on the data
        frame_view = memoryview(frame)
        # Scan all line
        for y in range(self.n_banks * self.n_rows):
            # Send write command to line buffer
            self.send_line_data(frame_view[y*self.line_bytes:(y+1)*self.line_bytes])
            # Swap line buffer & Write it to line y of back frame buffer
            self.reg_w8(0x03, y)

        # Send frame swap command
        self.reg_w8(0x04, 0x00)

        # Wait for the frame swap to occur
        while (self.read_status() & 0x02 == 0):
            pass

    def assemble_buffer(self, image):
        frame_buffer = bytearray(64*32*2)
        for x in range(image.width):
            for y in range(image.height):
                pixel = image.getpixel((x,y))
                # red and green values
                frame_buffer[y * 128 + x*2 + 1]= pixel[0] & 0xf8 | pixel[1] >> 5
                # blue values
                frame_buffer[y * 128 + x*2] = (pixel[1] << 5) & 0xe0 | pixel[2] >> 3
        return frame_buffer


def main():
    panel = PanelControl()
    update = updater.updater()
    update.start()
    while(True):
        frame_buffer = panel.assemble_buffer(update.get_draw_buffer())
        panel.send_frame_data(frame_buffer)
        time.sleep(1)

if __name__ == '__main__':
    main()
