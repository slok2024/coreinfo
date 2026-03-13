import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import os
import sys
import platform
import re

# --- 深度优化的全指令中文映射表 ---
# 包含指令、状态以及描述的全面翻译
TRANSLATE_DICT = {
    "HTT": "超线程技术 (Hyperthreading)",
    "CET": "控制流强制技术 (CET)",
    "KERNEL CET": "内核模式 CET 已启用",
    "USER CET": "用户模式 CET 已允许",
    "X64": "支持 64 位模式 (64-bit mode)",
    "SMX": "Intel 可信执行技术 (TXT)",
    "SKINIT": "AMD SKINIT 安全初始化",
    "SGX": "Intel 软件保护扩展 (SGX)",
    "NX": "NX/XD 执行禁止位 (内存保护)",
    "SMEP": "管理模式执行保护",
    "SMAP": "管理模式访问保护",
    "PAGE1GB": "支持 1GB 大页内存",
    "PAE": "支持大于 32 位物理地址",
    "PAT": "页属性表 (PAT)",
    "PSE": "支持 4MB 页面",
    "PSE36": "支持大于 32 位地址的 4MB 页面",
    "PGE": "页表中的全局位支持",
    "SS": "总线嗅探 (缓存操作)",
    "VME": "虚拟 8086 模式扩展",
    "RDWRFSGSBASE": "支持直接访问 GS/FS 寄存器基址",
    "FPU": "内置 i387 浮点运算单元",
    "MMX": "MMX 指令集",
    "MMXEXT": "AMD MMX 扩展指令",
    "3DNOW": "3DNow! 指令",
    "3DNOWEXT": "3DNow! 扩展指令",
    "SSE": "流式 SIMD 扩展 (SSE)",
    "SSE2": "流式 SIMD 扩展 2 (SSE2)",
    "SSE3": "流式 SIMD 扩展 3 (SSE3)",
    "SSSE3": "补充流式 SIMD 扩展 3 (SSSE3)",
    "SSE4A": "AMD SSE4a 指令",
    "SSE4.1": "流式 SIMD 扩展 4.1",
    "SSE4.2": "流式 SIMD 扩展 4.2",
    "AES": "AES 硬件加密加速",
    "AVX": "高级向量扩展 (AVX)",
    "AVX2": "高级向量扩展 2 (AVX2)",
    "AVX-512-F": "AVX-512 基础指令",
    "AVX-512-DQ": "AVX-512 双字/四字指令",
    "AVX-512-IFAMA": "AVX-512 整数融合乘加指令",
    "AVX-512-PF": "AVX-512 预取指令",
    "AVX-512-ER": "AVX-512 指数/倒数指令集",
    "AVX-512-CD": "AVX-512 冲突检测指令",
    "AVX-512-BW": "AVX-512 字节/字指令",
    "AVX-512-VL": "AVX-512 矢量长度指令",
    "FMA": "融合乘加指令 (FMA3)",
    "MSR": "模型特定寄存器读写 (RDMSR/WRMSR)",
    "MTRR": "内存类型范围寄存器",
    "XSAVE": "处理器状态保存/恢复指令",
    "OSXSAVE": "操作系统 XSAVE 支持",
    "RDRAND": "硬件随机数生成器",
    "RDSEED": "硬件种子生成器",
    "CMOV": "条件移动指令",
    "CLFSH": "缓存行刷新指令",
    "CX8": "8字节比较交换指令 (CMPXCHG8B)",
    "CX16": "16字节比较交换指令 (CMPXCHG16B)",
    "BMI1": "位操作指令集 1",
    "BMI2": "位操作指令集 2",
    "ADX": "大数运算指令扩展",
    "DCA": "直接缓存访问",
    "F16C": "半精度浮点转换指令",
    "FXSR": "快速浮点环境保存/恢复",
    "FFXSR": "优化的 FXSAVE/FSRSTOR",
    "MONITOR": "监视/等待指令 (MONITOR/MWAIT)",
    "MOVBE": "大端移动指令",
    "ERMSB": "增强型字符串处理 (REP MOVSB/STOSB)",
    "PCLMULDQ": "无进位乘法指令",
    "POPCNT": "位计数指令 (Population Count)",
    "LZCNT": "前导零计数指令",
    "SEP": "快速系统调用指令",
    "LAHF-SAHF": "64位模式下的 LAHF/SAHF 指令",
    "LAHF": "64位模式下的 LAHF/SAHF 指令",
    "HLE": "硬件锁定洗脱指令",
    "RTM": "受限事务内存指令",
    "DE": "调试扩展 (I/O 断点)",
    "DTES64": "64位分支跟踪存储",
    "DS": "调试存储器",
    "DS-CPL": "基于权限级的调试存储",
    "PCID": "进程上下文标识符 (PCID)",
    "INVPCID": "使 PCID 无效指令",
    "PDCM": "性能能力 MSR",
    "RDTSCP": "序列化读取时间戳计数器",
    "TSC": "读取时间戳计数器 (RDTSC)",
    "TSC-DEADLINE": "本地 APIC 支持定时器截止时间",
    "TSC-INVARIANT": "恒定频率时间戳计数器",
    "XTPR": "禁用任务优先级消息",
    "EIST": "Intel 增强型节能技术",
    "ACPI": "ACPI 电源管理 MSR",
    "TM": "热量监视器电路",
    "TM2": "热量监视器 2 控制",
    "APIC": "内置本地 APIC",
    "X2APIC": "支持 x2APIC",
    "CNXT-ID": "L1 数据缓存自适应模式",
    "MCE": "机器检查异常",
    "MCA": "机器检查架构",
    "PBE": "挂起中断请求支持",
    "PSN": "处理器序列号",
    "PREFETCHW": "支持 PREFETCHW 指令",
    "HYPERVISOR": "正在虚拟机/管理程序下运行",
    "VMX": "Intel 硬件虚拟化 (VT-x)",
    "EPT": "二级地址转换 (SLAT)",
    "URG": "Intel 无限制访客模式",
    "U-CET": "允许用户模式 CET",
    "K-CET": "已启用内核模式 CET"
}

class GoVersionExpertGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Coreinfo 硬件检测与 Go 版本判定")
        self.root.geometry("750x850")
        self.root.configure(bg="#f3f3f3")
        
        # --- 1. 顶部判定显示区 ---
        self.ver_frame = tk.LabelFrame(root, text=" 系统架构与 Go 编译判定 ", padx=15, pady=10, bg="#f3f3f3")
        self.ver_frame.pack(fill="x", padx=20, pady=10)
        
        self.result_var = tk.StringVar(value="等待检测...")
        self.lbl_result = tk.Label(self.ver_frame, textvariable=self.result_var, 
                                  font=("微软雅黑", 18, "bold"), fg="#555", bg="#f3f3f3")
        self.lbl_result.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        
        self.arch_var = tk.StringVar(value=f"系统架构: {platform.machine()}")
        self.lbl_arch = tk.Label(self.ver_frame, textvariable=self.arch_var, font=("微软雅黑", 9), fg="#666", bg="#f3f3f3")
        self.lbl_arch.grid(row=1, column=0, sticky="w")
        
        self.kernel_var = tk.StringVar(value="准备就绪")
        self.lbl_kernel = tk.Label(self.ver_frame, textvariable=self.kernel_var, font=("微软雅黑", 9, "italic"), fg="#0078d7", bg="#f3f3f3")
        self.lbl_kernel.grid(row=1, column=1, sticky="w", padx=20)

        # --- 2. 参数选择区域 ---
        options_frame = tk.LabelFrame(root, text=" 选择检测项目 ", padx=10, pady=10, bg="#f3f3f3")
        options_frame.pack(fill="x", padx=20)

        self.vars = {
            "-f": tk.BooleanVar(value=True),
            "-c": tk.BooleanVar(value=True),
            "-l": tk.BooleanVar(value=True),
            "-s": tk.BooleanVar(value=True),
            "-n": tk.BooleanVar(value=False),
            "-v": tk.BooleanVar(value=False),
        }

        descriptions = {
            "-f": "指令特征 (Features)", "-c": "核心信息 (Cores)",
            "-l": "缓存结构 (Caches)", "-s": "插槽信息 (Sockets)",
            "-n": "NUMA节点", "-v": "虚拟化支持"
        }

        for i, (arg, var) in enumerate(self.vars.items()):
            cb = tk.Checkbutton(options_frame, text=f"{arg} {descriptions[arg]}", variable=var, bg="#f3f3f3")
            cb.grid(row=i//3, column=i%3, sticky="w", padx=20, pady=2)

        # --- 3. 操作按钮 ---
        btn_frame = tk.Frame(root, bg="#f3f3f3")
        btn_frame.pack(pady=15)

        self.btn_run = tk.Button(btn_frame, text=" 执行检测 ", command=self.run_coreinfo, 
                                 bg="#0078d7", fg="white", font=("微软雅黑", 10, "bold"), 
                                 width=15, pady=5, relief="flat", cursor="hand2")
        self.btn_run.pack(side=tk.LEFT, padx=10)

        self.btn_clear = tk.Button(btn_frame, text=" 清 空 ", command=self.clear_all, 
                                 bg="#e1e1e1", fg="#333", font=("微软雅黑", 10),
                                 width=15, pady=5, relief="flat", cursor="hand2")
        self.btn_clear.pack(side=tk.LEFT, padx=10)

        # --- 4. 输出区 ---
        self.display = scrolledtext.ScrolledText(root, wrap=tk.NONE, font=("Consolas", 10), 
                                                bg="white", fg="#212529", borderwidth=1, relief="solid")
        self.display.pack(expand=True, fill='both', padx=20, pady=10)

        self.display.tag_config("supported", foreground="#1a7f37", font=("Consolas", 10, "bold"))
        self.display.tag_config("unsupported", foreground="#cf222e")
        self.display.tag_config("info", foreground="#0969da")

    def get_resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def get_coreinfo_exe(self):
        # 优化架构识别 logic
        arch = os.environ.get('PROCESSOR_ARCHITECTURE', '').upper()
        arch_ext = os.environ.get('PROCESSOR_ARCHITEW6432', '').upper()
        is_64bit = '64' in arch or '64' in arch_ext
        
        target_name = "Coreinfo64.exe" if is_64bit else "Coreinfo.exe"
        self.arch_var.set(f"系统架构: {'x64' if is_64bit else 'x86'} (环境变量识别)")
        self.kernel_var.set(f"当前内核: {target_name}")
        return self.get_resource_path(target_name)

    def translate_line(self, line):
        # 核心修正：模糊匹配指令并翻译
        # 匹配逻辑：找寻行首的指令关键词，然后保留状态符号，替换描述
        match = re.match(r'^([\w\-.]+)\s+([\*\-])\s*(.*)', line)
        if match:
            cmd, status, desc = match.groups()
            cmd_upper = cmd.upper()
            
            # 特殊处理：有些指令在 Coreinfo 输出里带连字符或空格
            # 在字典中查找翻译，如果找不到则保留原英文描述
            cn_desc = TRANSLATE_DICT.get(cmd_upper, desc.strip())
            
            # 重新拼装行，保证格式对齐
            return f"{cmd:<16} {status} {cn_desc}"
        
        # 处理非指令行（如标题）
        for key in ["Logical to Physical", "Logical Processor to Socket", "Logical Processor to Cache"]:
            if key in line:
                return line.replace("Logical to Physical Processor Map", "逻辑处理器到物理处理器映射") \
                           .replace("Logical Processor to Socket Map", "逻辑处理器到插槽映射") \
                           .replace("Logical Processor to Cache Map", "逻辑处理器到缓存映射")
        return line

    def run_coreinfo(self):
        exe_path = self.get_coreinfo_exe()
        if not os.path.exists(exe_path):
            messagebox.showerror("错误", f"找不到内核：{os.path.basename(exe_path)}")
            return

        cmd_args = ["-nobanner", "-accepteula"]
        for arg, var in self.vars.items():
            if var.get(): cmd_args.append(arg)
        
        try:
            creation_flags = 0x08000000 if platform.system() == "Windows" else 0
            process = subprocess.run([exe_path] + cmd_args, capture_output=True, text=False, creationflags=creation_flags)
            
            raw_data = process.stdout
            try:
                decoded = raw_data.decode('gbk', errors='ignore')
            except:
                decoded = raw_data.decode('utf-8', errors='ignore')
            
            # 清理非打印字符但保留中文编码
            output = "".join(c for c in decoded if (32 <= ord(c) <= 126) or c == '\n' or ord(c) > 127)
            self.update_go_level(output)

            self.display.delete(1.0, tk.END)
            for line in output.splitlines():
                if not line.strip(): continue
                
                # 翻译当前行
                display_line = self.translate_line(line)
                
                # 根据状态渲染颜色
                if " * " in display_line:
                    self.display.insert(tk.END, display_line + "\n", "supported")
                elif " - " in display_line:
                    self.display.insert(tk.END, display_line + "\n", "unsupported")
                elif ":" in display_line:
                    self.display.insert(tk.END, display_line + "\n", "info")
                else:
                    self.display.insert(tk.END, display_line + "\n")
            
        except Exception as e:
            self.display.insert(tk.END, f"执行异常: {str(e)}\n")

    def clear_all(self):
        self.display.delete(1.0, tk.END)
        self.result_var.set("等待检测...")
        self.lbl_result.config(fg="#555")

    def update_go_level(self, output):
        flags = {}
        # 为判定逻辑提供更宽松的正则
        matches = re.findall(r'^([\w\-.]+)\s*([\*\-])', output, re.MULTILINE)
        for name, status in matches:
            flags[name.upper()] = (status == '*')

        is_v2 = all([flags.get("SSE4.2"), flags.get("POPCNT"), flags.get("CX16"), flags.get("LAHF-SAHF") or flags.get("LAHF")])
        is_v3 = is_v2 and all([flags.get("AVX"), flags.get("AVX2"), flags.get("BMI1"), flags.get("BMI2"), flags.get("FMA"), flags.get("LZCNT")])
        is_v4 = is_v3 and any([flags.get("AVX-512-F"), flags.get("AVX-512F"), flags.get("AVX512F")])

        if is_v4:
            self.result_var.set("判定结果: GOAMD64=v4"); self.lbl_result.config(fg="#8250df")
        elif is_v3:
            self.result_var.set("判定结果: GOAMD64=v3"); self.lbl_result.config(fg="#0969da")
        elif is_v2:
            self.result_var.set("判定结果: GOAMD64=v2"); self.lbl_result.config(fg="#1a7f37")
        else:
            self.result_var.set("判定结果: GOAMD64=v1"); self.lbl_result.config(fg="#cf222e")

if __name__ == "__main__":
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    app = GoVersionExpertGUI(root)
    root.mainloop()