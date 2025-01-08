import ctypes
import win32api
import win32process
import win32con
import os
import time

# Fungsi untuk mendapatkan PID dari proses berdasarkan nama
def cari_pid(nama_proses):
    """Mencari PID dari proses yang berjalan berdasarkan nama."""
    try:
        proses = win32process.EnumProcesses()
        for pid in proses:
            try:
                h_proses = win32api.OpenProcess(
                    win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid
                )
                nama_exe = win32process.GetModuleFileNameEx(h_proses, 0)
                if nama_proses.lower() in nama_exe.lower():
                    win32api.CloseHandle(h_proses)
                    return pid
            except Exception:
                continue
    except Exception as e:
        tulis_log(f"Gagal mendapatkan daftar proses: {e}")
    return None

# Fungsi untuk mencatat aktivitas ke file log
def tulis_log(pesan):
    """Mencatat aktivitas ke file log."""
    with open("dump_log.txt", "a") as log_file:
        log_file.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {pesan}\n")

# Fungsi untuk mendump memori proses
def dump_memori(pid, nama_dll, file_output):
    """Dump memori proses target ke file output."""
    PROCESS_VM_READ = 0x0010
    PROCESS_QUERY_INFORMATION = 0x0400

    try:
        h_proses = win32api.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
        try:
            modul_list = win32process.EnumProcessModules(h_proses)
            for modul in modul_list:
                try:
                    nama_modul = win32process.GetModuleFileNameEx(h_proses, modul)
                    if nama_dll.lower() in nama_modul.lower():
                        base_addr = modul
                        mod_info = win32process.GetModuleInformation(h_proses, modul)
                        ukuran = mod_info[1]

                        tulis_log(f"Menemukan DLL {nama_modul} di alamat {hex(base_addr)}")

                        buffer = ctypes.create_string_buffer(ukuran)
                        bytes_dibaca = ctypes.c_size_t()

                        if ctypes.windll.kernel32.ReadProcessMemory(
                            h_proses,
                            ctypes.c_void_p(base_addr),
                            buffer,
                            ukuran,
                            ctypes.byref(bytes_dibaca),
                        ):
                            with open(file_output, "wb") as output_file:
                                output_file.write(buffer.raw[:bytes_dibaca.value])
                            tulis_log(f"Dump memori DLL {nama_modul} disimpan ke {file_output}")
                        else:
                            tulis_log(f"Gagal membaca memori dari {nama_modul}")
                except Exception as e:
                    tulis_log(f"Error saat memproses modul: {e}")
        finally:
            win32api.CloseHandle(h_proses)
    except Exception as e:
        tulis_log(f"Error: {e}")
        print(f"Error: {e}")

# Fungsi untuk mencetak daftar semua proses yang sedang berjalan
def daftar_proses():
    """Menampilkan daftar semua proses yang sedang berjalan."""
    print("\nDaftar Proses yang Sedang Berjalan:")
    tulis_log("Menampilkan daftar proses yang sedang berjalan")
    try:
        proses = win32process.EnumProcesses()
        for pid in proses:
            try:
                h_proses = win32api.OpenProcess(
                    win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid
                )
                try:
                    nama_exe = win32process.GetModuleFileNameEx(h_proses, 0)
                    print(f"PID: {pid} - Nama: {nama_exe}")
                finally:
                    win32api.CloseHandle(h_proses)
            except Exception:
                continue
    except Exception as e:
        tulis_log(f"Gagal mendapatkan daftar proses: {e}")

if __name__ == "__main__":
    print("\nAlat Dump Memori - Versi Canggih")
    print("=================================")

    pilihan = input("Pilih opsi:\n1. Dump memori proses\n2. Tampilkan daftar proses\nPilihan Anda: ")

    if pilihan == "1":
        nama_proses = input("Masukkan nama proses target (contoh: notepad.exe): ")
        nama_dll = input("Masukkan nama DLL target (contoh: user32.dll): ")
        file_output = input("Masukkan nama file output (contoh: dump_memory.bin): ")

        pid = cari_pid(nama_proses)

        if pid:
            print(f"Proses {nama_proses} ditemukan dengan PID {pid}.")
            tulis_log(f"Proses {nama_proses} ditemukan dengan PID {pid}.")

            dump_memori(pid, nama_dll, file_output)
        else:
            print(f"Proses {nama_proses} tidak ditemukan!")
            tulis_log(f"Proses {nama_proses} tidak ditemukan!")
    elif pilihan == "2":
        daftar_proses()
    else:
        print("Pilihan tidak valid!")
