import os
import zipfile
import threading
from tkinter import Tk, filedialog, messagebox, ttk, Label, StringVar, IntVar, Radiobutton


def compress_folder_gui():
    """带保存选项和进度提示的文件夹压缩器"""

    # === 初始化主窗口 ===
    root = Tk()
    root.title("文件夹压缩工具")
    root.geometry("420x220")
    root.resizable(False, False)

    status_text = StringVar(value="请选择要压缩的文件夹")
    Label(root, textvariable=status_text, wraplength=400, pady=10).pack()

    # === 保存方式选择 ===
    Label(root, text="选择压缩包保存方式：", font=("Arial", 10, "bold")).pack()
    save_mode = IntVar(value=0)  # 0=默认路径，1=自定义路径
    Radiobutton(root, text="默认：与原文件夹同级", variable=save_mode, value=0).pack()
    Radiobutton(root, text="自定义：选择保存文件夹", variable=save_mode, value=1).pack()

    # === 进度条 ===
    progress = ttk.Progressbar(root, mode="determinate", length=380)
    progress.pack(pady=8)

    # === 主按钮 ===
    def select_and_compress():
        folder_path = filedialog.askdirectory(title="选择要压缩的文件夹")
        if not folder_path:
            status_text.set("已取消选择。")
            return

        # 解析路径信息
        current_folder = os.path.basename(folder_path)
        parent_folder_path = os.path.dirname(folder_path)
        parent_folder = os.path.basename(parent_folder_path)
        zip_name = f"{parent_folder}_{current_folder}.zip"

        # 确定保存位置
        if save_mode.get() == 1:
            # 自定义保存路径
            save_path = filedialog.askdirectory(title="选择压缩包保存位置")
            if not save_path:
                status_text.set("未选择保存路径。")
                return
            zip_path = os.path.join(save_path, zip_name)
        else:
            # 默认保存路径
            zip_path = os.path.join(parent_folder_path, zip_name)

        # 检查文件是否存在
        if os.path.exists(zip_path):
            if not messagebox.askyesno("文件已存在", f"{zip_name} 已存在，是否覆盖？"):
                status_text.set("操作已取消。")
                return

        # === 压缩逻辑在线程中运行 ===
        def do_compress():
            try:
                # 获取所有文件
                all_files = []
                for root_dir, _, files in os.walk(folder_path):
                    for file in files:
                        all_files.append(os.path.join(root_dir, file))
                total = len(all_files)
                if total == 0:
                    messagebox.showwarning("提示", "该文件夹为空。")
                    return

                progress["maximum"] = total
                status_text.set("正在压缩，请稍候...")

                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for i, file_path in enumerate(all_files, start=1):
                        arcname = os.path.relpath(file_path, start=parent_folder_path)
                        zipf.write(file_path, arcname=arcname)
                        progress["value"] = i
                        root.update_idletasks()

                messagebox.showinfo("压缩完成", f"压缩包已生成：\n{zip_path}")
                status_text.set("压缩完成 ✅")

            except Exception as e:
                messagebox.showerror("错误", f"压缩失败：\n{e}")
                status_text.set("压缩失败 ❌")

        threading.Thread(target=do_compress, daemon=True).start()

    ttk.Button(root, text="选择文件夹并压缩", command=select_and_compress).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    compress_folder_gui()
