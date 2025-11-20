import os
import zipfile
import threading
from tkinter import Tk, filedialog, messagebox, ttk, Label, StringVar, IntVar, Radiobutton, Listbox, END, SINGLE, simpledialog

def compress_folder_gui():
    root = Tk()
    root.title("批量文件夹压缩工具")
    root.geometry("520x800")
    root.resizable(False, False)

    status_text = StringVar(value="请选择操作")
    Label(root, textvariable=status_text, wraplength=500, pady=10).pack()

    # 保存方式选择
    Label(root, text="压缩包保存位置选择：", font=("Arial", 10, "bold")).pack()
    save_mode = IntVar(value=0)
    Radiobutton(root, text="默认：与原文件夹同级", variable=save_mode, value=0).pack()
    Radiobutton(root, text="自定义：选择保存文件夹", variable=save_mode, value=1).pack()

    # 压缩规则选择
    Label(root, text="压缩规则选择：", font=("Arial", 10, "bold"), pady=5).pack()
    compress_mode = IntVar(value=0)
    Radiobutton(root, text="模式 A：父名_子名", variable=compress_mode, value=0).pack()
    Radiobutton(root, text="模式 B：父目录/子目录", variable=compress_mode, value=1).pack()

    # 路径列表框
    Label(root, text="已添加的文件夹路径：", font=("Arial", 10, "bold"), pady=5).pack()
    path_listbox = Listbox(root, width=70, height=12, selectmode=SINGLE)
    path_listbox.pack()

    # 双进度条
    Label(root, text="当前文件夹进度：").pack()
    progress_current = ttk.Progressbar(root, mode="determinate", length=480)
    progress_current.pack(pady=5)

    Label(root, text="总进度：").pack()
    progress_total = ttk.Progressbar(root, mode="determinate", length=480)
    progress_total.pack(pady=5)

    # === 按钮功能 ===
    def add_folder():
        folder = filedialog.askdirectory(title="选择文件夹")
        if folder:
            if folder not in path_listbox.get(0, END):
                path_listbox.insert(END, folder)
                status_text.set(f"已添加：{folder}")
            else:
                status_text.set("该路径已存在，已跳过")

    def clear_list():
        path_listbox.delete(0, END)
        status_text.set("已清空列表")

    def delete_selected():
        selection = path_listbox.curselection()
        if selection:
            index = selection[0]
            path_listbox.delete(index)
            status_text.set("已删除选中路径")

    def scan_folder_by_name():
        parent_folder = filedialog.askdirectory(title="选择要扫描的父目录")
        if not parent_folder:
            return
        folder_name = simpledialog.askstring("输入", "请输入要查找的文件夹名：")
        if not folder_name:
            status_text.set("未输入文件夹名")
            return

        found = []
        existing_paths = path_listbox.get(0, END)
        for root_dir, dirs, _ in os.walk(parent_folder):
            if folder_name in dirs:
                full_path = os.path.join(root_dir, folder_name)
                if full_path not in existing_paths:
                    path_listbox.insert(END, full_path)
                    found.append(full_path)
        if found:
            status_text.set(f"扫描完成，共找到 {len(found)} 个 '{folder_name}' 文件夹")
        else:
            status_text.set(f"未找到 '{folder_name}' 文件夹或已全部存在")

    # 批量压缩
    def start_compress():
        folders = path_listbox.get(0, END)
        if not folders:
            messagebox.showwarning("提示", "请先添加文件夹路径！")
            return

        if save_mode.get() == 1:
            save_path = filedialog.askdirectory(title="选择压缩包保存位置")
            if not save_path:
                status_text.set("未选择保存位置")
                return
        else:
            save_path = None

        progress_total["value"] = 0
        progress_total["maximum"] = len(folders)
        status_text.set("开始批量压缩...")

        def do_batch():
            for idx, folder_path in enumerate(folders, start=1):
                current_folder = os.path.basename(folder_path)
                parent_folder_path = os.path.dirname(folder_path)
                parent_folder = os.path.basename(parent_folder_path)

                if compress_mode.get() == 0:
                    zip_name = f"{parent_folder}_{current_folder}.zip"
                else:
                    zip_name = f"{parent_folder}.zip"

                if save_mode.get() == 1:
                    zip_path = os.path.join(save_path, zip_name)
                else:
                    zip_path = os.path.join(parent_folder_path, zip_name)

                try:
                    all_files = []
                    for root_dir, _, files in os.walk(folder_path):
                        for f in files:
                            all_files.append(os.path.join(root_dir, f))
                    total_files = len(all_files)
                    if total_files == 0:
                        messagebox.showwarning("提示", f"{folder_path} 是空文件夹，已跳过。")
                        progress_total["value"] = idx
                        root.update_idletasks()
                        continue

                    progress_current["maximum"] = total_files
                    progress_current["value"] = 0

                    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                        for i, file_path in enumerate(all_files, start=1):
                            if compress_mode.get() == 1:
                                arcname = os.path.relpath(file_path, start=parent_folder_path)
                            else:
                                arcname = os.path.relpath(file_path, start=folder_path)
                                arcname = os.path.join(current_folder, arcname)
                            zipf.write(file_path, arcname)
                            progress_current["value"] = i
                            root.update_idletasks()

                    progress_total["value"] = idx
                    progress_current["value"] = 0
                    status_text.set(f"完成：{zip_name}")
                    root.update_idletasks()
                except Exception as err:
                    messagebox.showerror("错误", f"压缩失败：{folder_path}\n{err}")

            messagebox.showinfo("完成", "所有文件夹已全部压缩完成！")
            status_text.set("批量压缩完成 ✔")

        threading.Thread(target=do_batch, daemon=True).start()

    # === 按钮布局 ===
    ttk.Button(root, text="添加路径", command=add_folder).pack(pady=5)
    ttk.Button(root, text="扫描文件夹", command=scan_folder_by_name).pack(pady=5)
    ttk.Button(root, text="删除选中路径", command=delete_selected).pack(pady=5)
    ttk.Button(root, text="清空列表", command=clear_list).pack(pady=5)
    ttk.Button(root, text="开始压缩", command=start_compress).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    compress_folder_gui()
