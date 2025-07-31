#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📏 PDF 좌표 측정 도구
- PDF 파일을 열고 마우스 클릭으로 좌표 측정
- 측정된 좌표를 JSON 형태로 저장
- 실시간 좌표 표시
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import json
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import os
from datetime import datetime

class PDFCoordinateMeasurementTool:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 좌표 측정 도구")
        self.root.geometry("1200x800")
        
        # 변수 초기화
        self.pdf_path = None
        self.pdf_doc = None
        self.current_page = 0
        self.zoom_factor = 2.0  # 확대 배율
        self.measured_coordinates = {}
        self.field_name_var = tk.StringVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI 구성"""
        # 메인 프레임
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 상단 컨트롤 프레임
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # PDF 파일 선택
        tk.Button(control_frame, text="PDF 파일 선택", command=self.load_pdf).pack(side=tk.LEFT, padx=(0, 10))
        
        # 페이지 네비게이션
        tk.Button(control_frame, text="이전 페이지", command=self.prev_page).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(control_frame, text="다음 페이지", command=self.next_page).pack(side=tk.LEFT, padx=(0, 10))
        
        # 확대/축소
        tk.Button(control_frame, text="확대", command=self.zoom_in).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(control_frame, text="축소", command=self.zoom_out).pack(side=tk.LEFT, padx=(0, 10))
        
        # 필드명 입력
        tk.Label(control_frame, text="필드명:").pack(side=tk.LEFT, padx=(0, 5))
        tk.Entry(control_frame, textvariable=self.field_name_var, width=15).pack(side=tk.LEFT, padx=(0, 10))
        
        # 좌표 저장
        tk.Button(control_frame, text="좌표 저장", command=self.save_coordinates).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(control_frame, text="좌표 불러오기", command=self.load_coordinates).pack(side=tk.LEFT)
        
        # 메인 컨텐츠 프레임
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 좌측: PDF 뷰어
        self.pdf_frame = tk.Frame(content_frame, bg="white", relief=tk.SUNKEN, bd=2)
        self.pdf_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # PDF 캔버스
        self.canvas = tk.Canvas(self.pdf_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 마우스 클릭 이벤트
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        
        # 우측: 좌표 정보
        info_frame = tk.Frame(content_frame, width=300)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y)
        info_frame.pack_propagate(False)
        
        # 현재 좌표 표시
        coord_frame = tk.LabelFrame(info_frame, text="현재 좌표", padx=10, pady=10)
        coord_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.coord_label = tk.Label(coord_frame, text="마우스를 움직여보세요", font=("Arial", 10))
        self.coord_label.pack()
        
        # 측정된 좌표 목록
        list_frame = tk.LabelFrame(info_frame, text="측정된 좌표", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 스크롤바가 있는 리스트박스
        list_scroll = tk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.coord_listbox = tk.Listbox(list_frame, yscrollcommand=list_scroll.set)
        self.coord_listbox.pack(fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.coord_listbox.yview)
        
        # 삭제 버튼
        tk.Button(list_frame, text="선택 항목 삭제", command=self.delete_selected_coordinate).pack(pady=(10, 0))
        
        # 상태바
        self.status_var = tk.StringVar()
        self.status_var.set("PDF 파일을 선택해주세요")
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def load_pdf(self):
        """PDF 파일 로드"""
        file_path = filedialog.askopenfilename(
            title="PDF 파일 선택",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.pdf_path = file_path
                self.pdf_doc = fitz.open(file_path)
                self.current_page = 0
                self.display_current_page()
                self.status_var.set(f"PDF 로드됨: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("오류", f"PDF 파일 로드 실패: {str(e)}")
    
    def display_current_page(self):
        """현재 페이지 표시"""
        if not self.pdf_doc:
            return
            
        try:
            page = self.pdf_doc[self.current_page]
            
            # 페이지를 이미지로 렌더링
            mat = fitz.Matrix(self.zoom_factor, self.zoom_factor)
            pix = page.get_pixmap(matrix=mat)
            
            # PIL 이미지로 변환
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            self.photo = ImageTk.PhotoImage(img)
            
            # 캔버스에 표시
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            
            self.status_var.set(f"페이지 {self.current_page + 1} / {len(self.pdf_doc)}")
            
        except Exception as e:
            messagebox.showerror("오류", f"페이지 표시 실패: {str(e)}")
    
    def on_canvas_click(self, event):
        """캔버스 클릭 이벤트"""
        if not self.pdf_doc:
            return
            
        # 캔버스 좌표를 PDF 좌표로 변환
        pdf_x = event.x / self.zoom_factor
        pdf_y = event.y / self.zoom_factor
        
        # 필드명 확인
        field_name = self.field_name_var.get().strip()
        if not field_name:
            messagebox.showwarning("경고", "필드명을 입력해주세요")
            return
        
        # 좌표 저장
        self.measured_coordinates[field_name] = {
            "x": round(pdf_x, 2),
            "y": round(pdf_y, 2),
            "font_size": 12  # 기본값
        }
        
        # 리스트 업데이트
        self.update_coordinate_list()
        
        # 클릭 위치에 마커 표시
        self.canvas.create_oval(
            event.x-5, event.y-5, event.x+5, event.y+5,
            fill="red", tags="marker"
        )
        self.canvas.create_text(
            event.x+10, event.y-10,
            text=field_name,
            fill="red",
            font=("Arial", 8),
            tags="marker"
        )
        
        self.status_var.set(f"좌표 저장: {field_name} ({pdf_x:.1f}, {pdf_y:.1f})")
    
    def on_mouse_move(self, event):
        """마우스 이동 이벤트"""
        if not self.pdf_doc:
            return
            
        # 캔버스 좌표를 PDF 좌표로 변환
        pdf_x = event.x / self.zoom_factor
        pdf_y = event.y / self.zoom_factor
        
        self.coord_label.config(text=f"PDF 좌표: ({pdf_x:.1f}, {pdf_y:.1f})")
    
    def update_coordinate_list(self):
        """좌표 리스트 업데이트"""
        self.coord_listbox.delete(0, tk.END)
        for field_name, coords in self.measured_coordinates.items():
            self.coord_listbox.insert(tk.END, f"{field_name}: ({coords['x']:.1f}, {coords['y']:.1f})")
    
    def delete_selected_coordinate(self):
        """선택된 좌표 삭제"""
        selection = self.coord_listbox.curselection()
        if selection:
            field_name = list(self.measured_coordinates.keys())[selection[0]]
            del self.measured_coordinates[field_name]
            self.update_coordinate_list()
            self.canvas.delete("marker")  # 마커도 삭제
    
    def save_coordinates(self):
        """좌표를 JSON 파일로 저장"""
        if not self.measured_coordinates:
            messagebox.showwarning("경고", "저장할 좌표가 없습니다")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="좌표 파일 저장",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.measured_coordinates, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("성공", f"좌표가 저장되었습니다: {file_path}")
            except Exception as e:
                messagebox.showerror("오류", f"좌표 저장 실패: {str(e)}")
    
    def load_coordinates(self):
        """좌표 파일 불러오기"""
        file_path = filedialog.askopenfilename(
            title="좌표 파일 불러오기",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.measured_coordinates = json.load(f)
                self.update_coordinate_list()
                messagebox.showinfo("성공", f"좌표를 불러왔습니다: {file_path}")
            except Exception as e:
                messagebox.showerror("오류", f"좌표 불러오기 실패: {str(e)}")
    
    def prev_page(self):
        """이전 페이지"""
        if self.pdf_doc and self.current_page > 0:
            self.current_page -= 1
            self.display_current_page()
    
    def next_page(self):
        """다음 페이지"""
        if self.pdf_doc and self.current_page < len(self.pdf_doc) - 1:
            self.current_page += 1
            self.display_current_page()
    
    def zoom_in(self):
        """확대"""
        self.zoom_factor *= 1.2
        self.display_current_page()
    
    def zoom_out(self):
        """축소"""
        self.zoom_factor /= 1.2
        self.display_current_page()

def main():
    """메인 함수"""
    root = tk.Tk()
    app = PDFCoordinateMeasurementTool(root)
    root.mainloop()

if __name__ == "__main__":
    import io  # BytesIO를 위해 필요
    main() 