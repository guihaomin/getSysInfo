import os
import time
from subprocess import Popen, PIPE
class metric:
    def __init__(self,sample_duration,device,interface=""):
        self.reads_per_sec=0
        self.writes_per_sec=0
        self.write_amount=0
        self.read_amount=0
        self.total_process=0
        self.sleeping_process=0
        self.running_process=0
        self.threads=0
        self.blocked_process=0
        self.sample_duration=sample_duration
        self.device=device
        self.deltas=[]
        self.cpu_times={}
        self.run_queue=0
        self.load_avgs=0
        self.disk_busy=0
        self.total_process=0
        self.blocked_process=0
        self.used_mem=0
        self.free_mem=0
        self.swap_total=0
        self.swap_in=0
        self.swap_out=0
        self.page_in=0
        self.page_out=0
        self.interface=interface
        self.recieve_bytes=0       #bytes persec
        self.transmit_bytes=0      #bytes persec
        self.recieve_packages=0    #count persec
        self.transmit_packages=0   #count persec
        self.connections=0
        self.disconnections=0
        self.connections_before=[]
    def reset(self):             #refresh all data
        self.get_after_sleeping()
        self.connection()
        self.mem_stats()
        self.cpu_percents()
        self.procs_blocked()
        self.sleepingNum()
        self.threadsNum()
        self.run_queue_length()
        self.load_avg()
        self.procs_running()
    def list_connection(self,connection_list):
        with open('/proc/net/tcp') as f:
            for line in f:
                if not line.strip(" ").startswith("sl"):
                    connection_list.append(str(line.split()[1])+str(line.split()[2]))
        with open('/proc/net/tcp6') as f:
            for line in f:
                if not line.strip(" ").startswith("sl"):
                    connection_list.append(str(line.split()[1])+str(line.split()[2]))
        with open('/proc/net/udp') as f:
            for line in f:
                if not line.strip(" ").startswith("sl"):
                    connection_list.append(str(line.split()[1])+str(line.split()[2]))
        with open('/proc/net/udp6') as f:
            for line in f:
                if not line.strip(" ").startswith("sl"):
                    connection_list.append(str(line.split()[1])+str(line.split()[2]))
    def connection(self):#this is weird the system log info(/proc/net/sockstat) is not same as info in count /proc/net/tcp, use info in tcp
        """with open('/proc/net/sockstat') as f:
            for line in f:
                if line.startswith('TCP:'):
                    tcp_connection=int(line.split()[2])
                elif line.startswith('UDP:'):
                    udp_connection=int(line.split()[2])
        with open('/proc/net/sockstat6') as f:
            for line in f:
                if line.startswith('TCP6:'):
                    tcp6_connection=int(line.split()[2])
                elif line.startswith('UDP6:'):
                    udp6_connection=int(line.split()[2])
        self.connections=tcp_connection+tcp6_connection+udp_connection+udp6_connection"""
        self.connections=len(self.connections_before)
        
    def mem_stats(self):
        with open('/proc/meminfo') as f:
            for line in f:
                if line.startswith('MemTotal:'):
                    mem_total = int(line.split()[1]) * 1024
                elif line.startswith('Active: '):
                    mem_active = int(line.split()[1]) * 1024
                elif line.startswith('MemFree:'):
                    mem_free = (int(line.split()[1]) * 1024)
                elif line.startswith('Cached:'):
                    mem_cached = (int(line.split()[1]) * 1024)
                elif line.startswith('SwapTotal: '):
                    swap_total = (int(line.split()[1]) * 1024)
                elif line.startswith('SwapFree: '):
                    swap_free = (int(line.split()[1]) * 1024)
        self.used_mem=(mem_total-mem_free)/float(mem_total)*100.0
        self.free_mem=mem_free/float(mem_total)*100.0
        self.swap_total=swap_total


    def cpu_percents(self):
    
        
        total = sum(self.deltas)
        percents = [100 - (100 * (float(total - x) / total)) for x in self.deltas]

        self.cpu_times={
            'user': percents[0],
            'nice': percents[1],
            'system': percents[2],
            'idle': percents[3],
            'iowait': percents[4],
            'irq': percents[5],
            'softirq': percents[6],
        }
    def get_after_sleeping(self): 
        """Return number of disk (reads, writes) per sec during the sample_duration."""
        connections_before=[]
        connections_after=[]

        readSum1=self.readSum()
        writeSum1=self.writeSum()
        
        with open('/proc/diskstats') as f1:
            with open('/proc/diskstats') as f2:
                
                f3=open('/proc/stat')      #open stat to read CPU INFO,f3(before sleeping, f4(after sleeping)
                f4=open('/proc/stat')
                
                with open('/proc/vmstat') as f:#page index before sleeping
                    for line in f:
                        if line.startswith('pgpgin'):  
                            page_in=int(line.split()[1])
                        elif line.startswith('pgpgout'):
                            page_out=int(line.split()[1])
                        elif line.startswith('pswpin'):
                            swap_in=int(line.split()[1])
                        elif line.startswith('pswpout'):
                            swap_out=int(line.split()[1])
                            
                for n1 in open('/proc/net/dev'):    #network info before sleeping
                    if self.interface in n1:
                        data = n1.split('%s:' % self.interface)[1].split()
                        rx_bytes, tx_bytes= (int(data[0]), int(data[8]))
                        rx_pack,tx_pack=(int(data[1]),int(data[9]))
                        
                line1=f3.readline()   #read CPU INFO
                
                content1 = f1.read()  #read disk INFO
                
                self.list_connection(self.connections_before)  #list connections
                
                time.sleep(float(self.sample_duration))

                self.list_connection(connections_after) #list connections and calculate disconnections number
                for item in self.connections_before:
                    if not item in connections_after:
                        self.disconnections+=1
                        
                content2 = f2.read() #read disk INFO
                
                with open('/proc/vmstat') as f:    #read page infos
                    for line in f:
                        if line.startswith('pgpgin'):
                            page_in2=int(line.split()[1])
                        elif line.startswith('pgpgout'):
                            page_out2=int(line.split()[1])
                        elif line.startswith('pswpin'):
                            swap_in2=int(line.split()[1])
                        elif line.startswith('pswpout'):
                            swap_out2=int(line.split()[1])
                #calculate page info result
                self.page_in=1.0*(page_in2-page_in)/self.sample_duration
                self.page_out=1.0*(page_out2-page_out)/self.sample_duration
                self.swap_in=1.0*(swap_in2-swap_in)/self.sample_duration
                self.swap_out=1.0*(swap_out2-swap_out)/self.sample_duration
                #read network info
                for n1 in open('/proc/net/dev'):
                    if self.interface in n1:
                        data = n1.split('%s:' % self.interface)[1].split()
                        rx_bytes2, tx_bytes2= (int(data[0]), int(data[8]))
                        rx_pack2,tx_pack2=(int(data[1]),int(data[9]))

                #calculate network info
                self.recieve_bytes=rx_bytes2-rx_bytes
                self.transmit_bytes=tx_bytes2-tx_bytes
                self.recieve_packages=rx_pack2-rx_pack
                self.transmit_packages=tx_pack2-tx_pack
                self.transmit_packages/=float(self.sample_duration)
                self.recieve_packages/=float(self.sample_duration)
                self.recieve_bytes/=float(self.sample_duration)
                self.transmit_bytes/=float(self.sample_duration)
                
                line2=f4.readline()  #read CPU infos
                f3.close()
                f4.close()
        self.deltas = [int(b) - int(a) for a, b in zip(line1.split()[1:], line2.split()[1:])]       #deltas is used in CPU_percents to calculate CPU info

        #read total disk read counts
        readSum2=self.readSum()
        writeSum2=self.writeSum()

        #read disk work info and calculate results
        sep = '%s ' % self.device
        found = False
        for line in content1.splitlines():
            if sep in line:
                found = True
                fields = line.strip().split(sep)[1].split()
                num_reads1 = int(fields[0])
                num_writes1 = int(fields[4])
                break
        if not found:
            raise DiskError('device not found: %r' % device)
        for line in content2.splitlines():
            if sep in line:
                fields = line.strip().split(sep)[1].split()
                num_reads2 = int(fields[0])
                num_writes2 = int(fields[4])
                break            
        reads_per_sec = (num_reads2 - num_reads1) / float(self.sample_duration)
        writes_per_sec = (num_writes2 - num_writes1) / float(self.sample_duration)
        self.reads_per_sec=reads_per_sec
        self.writes_per_sec=writes_per_sec
        self.read_amount=readSum2-readSum1
        self.write_amount=writeSum2-writeSum1
        sep = '%s ' % self.device
        found = False
        for line in content1.splitlines():
            if sep in line:
                found = True
                io_ms1 = line.strip().split(sep)[1].split()[9]
                break
        if not found:
            raise DiskError('device not found: %r' % device)
        for line in content2.splitlines():
            if sep in line:
                io_ms2 = line.strip().split(sep)[1].split()[9]
                break            
        delta = int(io_ms2) - int(io_ms1)
        total = int(self.sample_duration) * 1000
        self.disk_busy=100 * (float(delta) / total)
    def parseDirD(self):     #return all the io file path for all pids
        list=[]
        self.total_process=0
        files=os.listdir("/proc")
        for file in files:
            m=os.path.join("/proc",file)
            if(os.path.isdir(m) and file.isdigit()):
                list.append(os.path.join(m,"io"))
                self.total_process+=1
        return list
    def readSum(self):   #calculate sum of all disk_read bytes
        total=0
        pids=self.parseDirD()
        for process in pids:
            if os.path.isfile(process):
                total+=int(self.__pid_stat("read_bytes:",process))
        return total
    def writeSum(self):    #calculate sum of all disk_write bytes
        total=0
        pids=self.parseDirD()
        for process in pids:
            if os.path.isfile(process):
                total+=float(self.__pid_stat("write_bytes:",process))
        return total
    def __pid_stat(self,stat,dir="/proc/stat"):  #get assigned information in assigned file(/proc/stat default)
        with open(dir) as f:
            for line in f:
                if line.startswith(stat):
                    return line.split()[1]
    def parseDir(self):              #return all the status file path for all pids
        list=[]
        self.total_process=0
        files=os.listdir("/proc")
        for file in files:
            m=os.path.join("/proc",file)
            if(os.path.isdir(m) and file.isdigit()):
                self.total_process+=1
                list.append(os.path.join(m,"status"))
        return list
    def procs_blocked(self):
        self.blocked_process=int(self.__pid_stat('procs_blocked'))
    def procs_running(self):
        self.running_process=int(self. __pid_stat('procs_running'))
    def sleepingNum(self):
        count=0
        pids=self.parseDir()
        for process in pids:
            if os.path.isfile(process):
                if self.__pid_stat("State:",process)=='S':
                    count+=1
        self.sleeping_process=count
    def threadsNum(self):
        count=0
        pids=self.parseDir()
        for process in pids:
            if os.path.isfile(process):
                count+=int(self.__pid_stat("Threads:",process))
        self.threads=count
    def run_queue_length(self):
        f=open("/proc/loadavg")
        set=f.readline().split()
        self.run_queue=int(set[3][0:set[3].find('/')])
    def load_avg(self):
        with open('/proc/loadavg') as f:
            line = f.readline()
    
        self.load_avgs = [float(x) for x in line.split()[:3]]

#a.disk_reads_writes_info()

#print a.recieve_bytes/1024.0
#print a.transmit_bytes/1024.0
#print a.transmit_packages
#a.mem_stats()
#a.cpu_percents()
#print a.free_mem
