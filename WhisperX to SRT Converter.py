import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import re
import os
import json
import threading
from datetime import datetime

class WhisperXToSRTConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("WhisperX to SRT Converter v3.0")
        self.root.geometry("750x580")
        self.root.minsize(650, 500)
        self.root.resizable(True, True)
        
        # 마테리얼 디자인 색상
        self.colors = {
            'primary': '#1976D2', 
            'primary_dark': '#1565C0',
            'surface': '#FFFFFF', 
            'background': '#F5F5F5',
            'success': '#4CAF50', 
            'warning': '#FF9800', 
            'error': '#F44336',
            'text': '#212121', 
            'text_light': '#757575', 
            'border': '#E0E0E0'
        }
        
        self.config_file = "converter_config.json"
        self.config = self.load_config()
        self.setup_gui()
        
    def load_config(self):
        """설정 로드"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {
            'output_path': '', 
            'save_output_path': True, 
            'include_speaker': True, 
            'offset': 0.0, 
            'min_duration': 1.0
        }
        
    def save_config(self):
        """설정 저장"""
        try:
            config = {
                'output_path': self.output_path_var.get() if self.save_path_var.get() else '',
                'save_output_path': self.save_path_var.get(),
                'include_speaker': self.include_speaker_var.get(),
                'offset': self.offset_var.get(),
                'min_duration': self.min_duration_var.get()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except:
            pass
            
    def create_styled_frame(self, parent, **kwargs):
        """스타일이 적용된 프레임 생성"""
        frame = tk.Frame(parent, bg=self.colors['surface'], relief='solid', bd=1, **kwargs)
        return frame
        
    def create_button(self, parent, text, command, style='primary', **kwargs):
        """스타일 버튼 생성"""
        colors = {
            'primary': (self.colors['primary'], 'white'),
            'secondary': (self.colors['surface'], self.colors['primary']),
            'success': (self.colors['success'], 'white')
        }
        bg, fg = colors.get(style, colors['primary'])
        
        return tk.Button(
            parent, text=text, command=command, bg=bg, fg=fg,
            font=('Segoe UI', 10, 'bold' if style == 'primary' else 'normal'),
            relief='flat', bd=0, cursor='hand2', padx=15, pady=6, **kwargs
        )
        
    def setup_gui(self):
        """GUI 구성"""
        self.root.configure(bg=self.colors['background'])
        
        # 메인 컨테이너
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # 타이틀
        title_frame = self.create_styled_frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            title_frame, text="🎬 WhisperX to SRT Converter",
            bg=self.colors['surface'], fg=self.colors['text'],
            font=('Segoe UI', 16, 'bold')
        ).pack(pady=10)
        
        # 탭 노트북
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 탭 1: 파일 설정
        files_frame = self.create_styled_frame(notebook)
        notebook.add(files_frame, text="📁 파일 설정")
        self.setup_files_tab(files_frame)
        
        # 탭 2: 변환 옵션
        options_frame = self.create_styled_frame(notebook)
        notebook.add(options_frame, text="⚙️ 옵션")
        self.setup_options_tab(options_frame)
        
        # 탭 3: 로그
        log_frame = self.create_styled_frame(notebook)
        notebook.add(log_frame, text="📋 로그")
        self.setup_log_tab(log_frame)
        
        # 하단 액션 바
        self.setup_action_bar(main_frame)
        
    def setup_files_tab(self, parent):
        """파일 설정 탭"""
        parent.configure(padx=20, pady=15)
        
        # 입력 파일
        tk.Label(
            parent, text="📥 입력 파일", bg=self.colors['surface'], 
            fg=self.colors['text'], font=('Segoe UI', 11, 'bold')
        ).pack(anchor=tk.W)
        
        input_frame = tk.Frame(parent, bg=self.colors['surface'])
        input_frame.pack(fill=tk.X, pady=(5, 15))
        
        self.file_path_var = tk.StringVar()
        tk.Entry(
            input_frame, textvariable=self.file_path_var, bg='white', 
            font=('Segoe UI', 9)
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.create_button(input_frame, "선택", self.select_input_file).pack(side=tk.RIGHT)
        
        # 출력 폴더
        tk.Label(
            parent, text="📤 출력 폴더", bg=self.colors['surface'], 
            fg=self.colors['text'], font=('Segoe UI', 11, 'bold')
        ).pack(anchor=tk.W)
        
        output_frame = tk.Frame(parent, bg=self.colors['surface'])
        output_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.output_path_var = tk.StringVar(value=self.config.get('output_path', ''))
        tk.Entry(
            output_frame, textvariable=self.output_path_var, bg='white', 
            font=('Segoe UI', 9)
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.create_button(output_frame, "선택", self.select_output_folder).pack(side=tk.RIGHT)
        
        self.save_path_var = tk.BooleanVar(value=self.config.get('save_output_path', True))
        tk.Checkbutton(
            parent, text="경로 기억하기", variable=self.save_path_var,
            bg=self.colors['surface'], fg=self.colors['text'], 
            font=('Segoe UI', 9)
        ).pack(anchor=tk.W, pady=(5, 15))
        
        # 미리보기 버튼
        self.create_button(parent, "👀 미리보기", self.preview_conversion, 'secondary').pack(pady=10)
        
    def setup_options_tab(self, parent):
        """옵션 설정 탭"""
        parent.configure(padx=20, pady=15)
        
        # 화자 구분
        self.include_speaker_var = tk.BooleanVar(value=self.config.get('include_speaker', True))
        tk.Checkbutton(
            parent, text="👥 화자 구분 포함 (SPEAKER_XX)", 
            variable=self.include_speaker_var, bg=self.colors['surface'], 
            fg=self.colors['text'], font=('Segoe UI', 10)
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # 고급 옵션들
        options_grid = tk.Frame(parent, bg=self.colors['surface'])
        options_grid.pack(fill=tk.X, pady=10)
        
        # 타임스탬프 오프셋
        tk.Label(
            options_grid, text="⏰ 타임스탬프 오프셋 (초)", bg=self.colors['surface'], 
            fg=self.colors['text'], font=('Segoe UI', 10)
        ).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        self.offset_var = tk.DoubleVar(value=self.config.get('offset', 0.0))
        tk.Entry(
            options_grid, textvariable=self.offset_var, width=8, bg='white'
        ).grid(row=0, column=1)
        
        # 최소 지속시간
        tk.Label(
            options_grid, text="⏱️ 최소 지속시간 (초)", bg=self.colors['surface'], 
            fg=self.colors['text'], font=('Segoe UI', 10)
        ).grid(row=1, column=0, sticky=tk.W, pady=(10, 0), padx=(0, 20))
        
        self.min_duration_var = tk.DoubleVar(value=self.config.get('min_duration', 1.0))
        tk.Entry(
            options_grid, textvariable=self.min_duration_var, width=8, bg='white'
        ).grid(row=1, column=1, pady=(10, 0))
        
    def setup_log_tab(self, parent):
        """로그 탭"""
        parent.configure(padx=10, pady=10)
        
        # 로그 텍스트
        self.log_text = scrolledtext.ScrolledText(
            parent, height=15, bg='white', 
            fg=self.colors['text'], font=('Consolas', 8), 
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 로그 지우기 버튼
        self.create_button(parent, "🗑️ 로그 지우기", self.clear_log, 'secondary').pack()
        
    def setup_action_bar(self, parent):
        """하단 액션 바"""
        action_frame = self.create_styled_frame(parent)
        action_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 상단: 변환 버튼과 진행률
        top_action = tk.Frame(action_frame, bg=self.colors['surface'])
        top_action.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        self.convert_button = self.create_button(top_action, "🚀 SRT로 변환", self.start_conversion)
        self.convert_button.pack(side=tk.LEFT)
        
        # 진행률 바
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            top_action, variable=self.progress_var, 
            maximum=100, length=200
        )
        self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 하단: 상태
        self.status_var = tk.StringVar(value="✅ 준비 완료")
        tk.Label(
            action_frame, textvariable=self.status_var, bg=self.colors['surface'], 
            fg=self.colors['success'], font=('Segoe UI', 9, 'bold')
        ).pack(pady=(0, 10))
        
        # 초기 로그
        self.log_message("🎉 WhisperX to SRT Converter v3.0 준비 완료!")
        
    def log_message(self, message):
        """로그 메시지 추가"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """로그 지우기"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("🗑️ 로그가 정리되었습니다.")
        
    def select_input_file(self):
        """입력 파일 선택"""
        file_path = filedialog.askopenfilename(
            title="WhisperX 텍스트 파일 선택",
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.log_message(f"📁 입력 파일: {os.path.basename(file_path)}")
            
    def select_output_folder(self):
        """출력 폴더 선택"""
        folder_path = filedialog.askdirectory(title="출력 폴더 선택")
        if folder_path:
            self.output_path_var.set(folder_path)
            self.log_message(f"📂 출력 폴더: {folder_path}")
            if self.save_path_var.get():
                self.save_config()
                
    def parse_whisperx_line(self, line):
        """WhisperX 라인 파싱"""
        pattern = r'\[(\d{2}:\d{2}:\d{2},\d{3})\]\s*(SPEAKER_\d+):\s*(.+)'
        match = re.match(pattern, line.strip())
        return match.groups() if match else (None, None, None)
        
    def timestamp_to_seconds(self, timestamp):
        """타임스탬프를 초로 변환"""
        time_part, ms_part = timestamp.split(',')
        h, m, s = map(int, time_part.split(':'))
        return h * 3600 + m * 60 + s + int(ms_part) / 1000
        
    def seconds_to_timestamp(self, seconds):
        """초를 SRT 타임스탬프로 변환"""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        ms = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"
        
    def convert_to_srt(self, input_file, output_file):
        """변환 로직"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            segments = []
            for i, line in enumerate(lines):
                self.progress_var.set((i / len(lines)) * 50)
                self.root.update_idletasks()
                
                timestamp, speaker, text = self.parse_whisperx_line(line)
                if timestamp and text:
                    start_seconds = self.timestamp_to_seconds(timestamp) + self.offset_var.get()
                    final_text = f"{speaker}: {text}" if self.include_speaker_var.get() else text
                    segments.append({'start': start_seconds, 'text': final_text})
                    
            if not segments:
                raise ValueError("변환할 자막 데이터를 찾을 수 없습니다.")
                
            # SRT 파일 생성
            with open(output_file, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(segments):
                    self.progress_var.set(50 + (i / len(segments)) * 50)
                    self.root.update_idletasks()
                    
                    start_time = segment['start']
                    end_time = (segments[i + 1]['start'] - 0.1 if i < len(segments) - 1 
                              else start_time + self.min_duration_var.get())
                    
                    if end_time - start_time < self.min_duration_var.get():
                        end_time = start_time + self.min_duration_var.get()
                        
                    f.write(f"{i + 1}\n")
                    f.write(f"{self.seconds_to_timestamp(start_time)} --> {self.seconds_to_timestamp(end_time)}\n")
                    f.write(f"{segment['text']}\n\n")
                    
            return True, f"성공! 자막 변환 완료"
            
        except Exception as e:
            return False, f"변환 오류: {str(e)}"
            
    def preview_conversion(self):
        """미리보기"""
        if not self.file_path_var.get():
            messagebox.showwarning("경고", "입력 파일을 선택해주세요.")
            return
            
        try:
            with open(self.file_path_var.get(), 'r', encoding='utf-8') as f:
                lines = f.readlines()[:3]
                
            preview = "=== 변환 미리보기 ===\n\n"
            for i, line in enumerate(lines):
                timestamp, speaker, text = self.parse_whisperx_line(line)
                if timestamp and text:
                    final_text = f"{speaker}: {text}" if self.include_speaker_var.get() else text
                    start_seconds = self.timestamp_to_seconds(timestamp) + self.offset_var.get()
                    end_seconds = start_seconds + self.min_duration_var.get()
                    
                    preview += f"{i + 1}\n"
                    preview += f"{self.seconds_to_timestamp(start_seconds)} --> "
                    preview += f"{self.seconds_to_timestamp(end_seconds)}\n"
                    preview += f"{final_text}\n\n"
                    
            messagebox.showinfo("🔍 미리보기", preview)
            
        except Exception as e:
            messagebox.showerror("오류", f"미리보기 오류: {str(e)}")
            
    def start_conversion(self):
        """변환 시작"""
        if not self.file_path_var.get() or not self.output_path_var.get():
            messagebox.showwarning("경고", "파일과 출력 폴더를 모두 선택해주세요.")
            return
            
        input_filename = os.path.basename(self.file_path_var.get())
        output_file = os.path.join(
            self.output_path_var.get(), 
            os.path.splitext(input_filename)[0] + ".srt"
        )
        
        self.save_config()
        self.convert_button.config(state=tk.DISABLED)
        self.status_var.set("🔄 변환 중...")
        
        def conversion_thread():
            try:
                self.log_message("🚀 변환 시작...")
                success, message = self.convert_to_srt(self.file_path_var.get(), output_file)
                
                if success:
                    self.log_message(f"✅ {message}")
                    self.status_var.set("✅ 변환 완료!")
                    messagebox.showinfo("완료", message)
                else:
                    self.log_message(f"❌ {message}")
                    self.status_var.set("❌ 변환 실패")
                    messagebox.showerror("오류", message)
                    
            except Exception as e:
                error_msg = f"예상치 못한 오류: {str(e)}"
                self.log_message(f"❌ {error_msg}")
                self.status_var.set("❌ 오류 발생")
                messagebox.showerror("오류", error_msg)
                
            finally:
                self.convert_button.config(state=tk.NORMAL)
                self.progress_var.set(0)
        
        threading.Thread(target=conversion_thread, daemon=True).start()

def main():
    try:
        root = tk.Tk()
        app = WhisperXToSRTConverter(root)
        
        def on_closing():
            app.save_config()
            root.destroy()
            
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
        
    except Exception as e:
        print(f"프로그램 실행 오류: {e}")
        input("아무 키나 누르세요...")

if __name__ == "__main__":
    main()
