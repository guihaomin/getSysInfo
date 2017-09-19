import linux_metrics as lm
import time
#need sudo
DISK_DEVICE="sda"
sample_duration=1
def stdPrint():
    f=open("data.txt","w")
    f.write(time.asctime( time.localtime(time.time()) )+"\n")
    f.write("metric Unit Tool/Source Monitoring_Interval(sec) is_Cumulative Priority Transformation Desception\n")
    writeCPU(f)
    writeProcess(f)
    writeMem(f)
    writeDisk(f)
    
    f.close()

def writeCPU(f):
    
    f.write("System_CPU_Usage ")
    cpu_stat = lm.cpu_stat.cpu_percents(sample_duration)
    sysUtil=cpu_stat['system']
    f.write(str(sysUtil)+" ")
    f.write("% ")
    f.write("cgoldberg ")
    f.write(str(sample_duration))
    f.write("\nUser_CPU_Usage ")
    userUtil=cpu_stat['user']
    f.write(str(userUtil)+" ")
    f.write("% ")
    f.write("cgoldberg ")
    f.write(str(sample_duration))
    f.write("\nLoad_Avg ")
    f2=open("/proc/loadavg")
    set=f2.readline().split()
    f2.close()
    f.write(set[1]+" ")
    f.write("cnt ")
    f.write("build_in ")
    f.write("300")
    f.write("\nRun_Queue_Length ")
    f.write(set[3][0:set[3].find('/')]+" ")
    f.write("cnt ")
    f.write("build_in ")
    f.write("NIL")
def writeProcess(f):
    f.write("\nTotal#Process ")     # it is the number of process since boot
    f.write(str(lm.cpu_stat.procs_all())+" ")
    f.write("cnt ")
    f.write("add ")
    f.write("NIL")
    f.write("\nRuning#Process ")
    f.write(str(lm.cpu_stat.procs_running())+" ")
    f.write("cnt ")
    f.write("cgoldberg ")
    f.write("NIL")
    f.write("\nSleeping#Process ")
    f.write(str(lm.cpu_stat.sleepingNum())+" ")
    f.write("cnt ")
    f.write("add ")
    f.write("NIL")
    f.write("\n#Threads ")
    f.write(str(lm.cpu_stat.threadsNum())+" ")
    f.write("cnt ")
    f.write("add ")
    f.write("NIL")
    f.write("\nBlocked#Process ")
    f.write(str(lm.cpu_stat.procs_blocked())+" ")
    f.write("cnt ")
    f.write("cgoldberg ")
    f.write("NIL")
def writeDisk(f):
    f.write("\n#Pysical_Disk_Read ")
    numRead,numWrite,amountRead,amountWrite=lm.disk_stat.disk_reads_writes_info(DISK_DEVICE,sample_duration)
    f.write(str(numRead)+" ")
    f.write("cnt ")
    f.write("cgoldberg ")
    f.write("1")
    f.write("\n#Pysical_Disk_Write ")
    f.write(str(numWrite)+" ")
    f.write("cnt ")
    f.write("cgoldberg ")
    f.write("1 ")
    f.write("\nAmount_Disk_Read ")
    f.write(str(amountRead)+" ")
    f.write("kb ")
    f.write("merge ")
    f.write("1")
    f.write("\nAmount_Disk_Write ")
    f.write(str(amountWrite)+" ")
    f.write("kb ")
    f.write("merge ")
    f.write("1")

def writeMem(f):
    stat=lm.mem_stat.mem_stats()
    memTotal=stat[1]
    memFree=stat[3]
    memUsed=memTotal-memFree
    f.write("\nUsed Physical Memory ")
    f.write(str(memUsed*100.0/memTotal)+" ")
    f.write("% ")
    f.write("cgoldberg ")
    f.write("NIL")
    f.write("\nUnused Pysical Memory ")
    f.write(str(memFree*100.0/memTotal)+" ")
    f.write("% ")
    f.write("cgoldberg ")
    f.write("NIL")
    
stdPrint()
    
    
    
