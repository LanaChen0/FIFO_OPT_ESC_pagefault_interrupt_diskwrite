#!/usr/bin/env python
# coding: utf-8

# My AOS Homework: To compare different reference strings(RANDOM,LOCALITY,MYSTR)' pafe fault,
# interrupt, disk write perform in different agorithm(FIFO,OPT,ESC,MYALGO).

#update:2019/11/20
#Author:Lana Chen
#Word Description:
#pf:page fault, it:interrupt, dw:disk write, reflist: reference string/list(My homework use "string"  but it doesn't matter.)
#dblist: dirty bit list

import random
import matplotlib.pyplot as plt

def CreateStr(reflist_mode):
    reflist=[]
    if reflist_mode == 'RANDOM':
        for i in range(100000):
            reflist.append( random.randint(1,501) )
    elif reflist_mode == 'LOCALITY':
        i=0
        while i < 100000:
            random_num = random.randint(1,501)
            random_loc = random_num + random.randint(25,51)
            if random_loc > 100000:
                random_loc = 100000
            for j in range(random_num, random_loc):
                reflist.append(j)
                i+=1
    elif reflist_mode == 'MYSTR':
        i=0
        while i < 100000:
            random_num = random.randint(1,501)
            for j in range(random_num,501):
                reflist.append(j)
                i+=1
    return reflist

def CreateFrame_RandomDirty(reflist,frame_size):
    frame=[];db_list=[];
    for i in range(frame_size):
        frame.append(reflist[i])
        db_list.append(random.randint(0,1))
    return frame,db_list

def CreateRefDirtyBit(frame_size):
    ref_bit_list=[];dirty_bit_list=[];
    for i in range(frame_size):
        ref_bit_list.append(1)
        dirty_bit_list.append(random.randint(0,1))
    return ref_bit_list,dirty_bit_list

def IfPageFault(i,reflist,frame,frame_size):
    for j in range(frame_size):
        if frame[j] == reflist[i]:
            return False
    return True

def PeekHighestPriority(ref_bit_list,dirty_bit_list,frame_size):
    for i in range(frame_size):
        if ref_bit_list[i]==0 and dirty_bit_list[i]==0:
            return 0,i
    for i in range(frame_size):
        if ref_bit_list[i]==0 and dirty_bit_list[i]==1:
            return 1,i
    for i in range(frame_size):
        if ref_bit_list[i]==1 and dirty_bit_list[i]==0:
            return 2,i
    for i in range(frame_size):
        if ref_bit_list[i]==1 and dirty_bit_list[i]==1:
            return 3,i

def FIFO(reflist,frame_size):
    frame,db_list= CreateFrame_RandomDirty(reflist,frame_size)
    pf=frame_size
    it=0
    dw=0
    replace_index=0
    for i in range(frame_size,100000):
        #check if page fault happen
        if IfPageFault(i,reflist,frame,frame_size):
            it+=1
            pf+=1
            frame[replace_index] = reflist[i]
            replace_index+=1
            if replace_index >= frame_size:
                replace_index=0
            #when page fault happened and also dirty bit = 1, then do disk write! 
            if db_list[replace_index] == 1:
                dw+=1
                db_list[replace_index] = 0
            else:
                db_list[replace_index] = 1
    return pf,it,dw

def OPT(reflist,frame_size):
    frame,db_list= CreateFrame_RandomDirty(reflist,frame_size)
    pf=frame_size
    it=0
    dw=0
    for i in range(100000):
        #check if page fault happens
        if IfPageFault(i,reflist,frame,frame_size):
            it+=1
            pf+=1
            #choose victim page from the page frame, use OPT concept!
            #record future might loc in frame, create l to store them.
            l=[]
            for j in range(frame_size):
                for k in range(i,100000):
                    loc=100000
                    if frame[j] == reflist[k]:
                        loc = j
                        break
                l.append(loc)
            #find the farest loc in l, the index of it is which we want to replace.
            FAR=0
            FAR_index=0
            for j in range(frame_size):
                if l[j] > FAR:
                    FAR = l[j]
                    FAR_index=j    
            #replace it
            frame[FAR_index] = reflist[i]
            #See if dirty bit=1 when page fault happens, if it is, then disk write.
            if db_list[FAR_index] == 1:
                dw+=1
                db_list[FAR_index] = 0
            else:
                db_list[FAR_index] = 1
    return pf,it,dw

#My strategy: by default, ref_bit are all 1, but dirty_bit are 0 or 1 by random.
#default:(ref,dir)=(1,0)/(1,1)
#one path and one cycle in topology of ESC:
#path: (1,0)=>(0,0)
#cycle: (0,1)=>(0,0)=>(1,1)=>(0,1)
#Victim page priority:(0,0)>(0,1)>(1,0)>(1,1)
def ESC(reflist,frame_size):
    #In ESC algo. db_list is useless but still need to call CreateFrame_RandomDirty() for creating frame
    frame,db_list= CreateFrame_RandomDirty(reflist,frame_size)
    ref_bit_list,dirty_bit_list = CreateRefDirtyBit(frame_size)
    pf=frame_size
    it=0
    dw=0
    for i in range(100000):
        #check if page fault happens
        if IfPageFault(i,reflist,frame,frame_size):
            it+=1
            pf+=1
            #choose victim page from the page frame, use ESC concept!
            php, loc = PeekHighestPriority(ref_bit_list,dirty_bit_list,frame_size)
            frame[loc]=reflist[i]
            #the following four cases all need to replace.
            #logically, if run out of (0,0), then use (0,1),(1,0) and so on. 
            if php==0:
                ref_bit_list[loc]=1
                dirty_bit_list[loc]=1
            elif php==1:
                dw+=1
                ref_bit_list[loc]=0
                dirty_bit_list[loc]=0
            elif php==2:
                ref_bit_list[loc]=0
                dirty_bit_list[loc]=0
            else:
                dw+=1
                ref_bit_list[loc]=0
                dirty_bit_list[loc]=1
    return pf,it,dw

#My strategy: Adapt OPT for running faster: check future only for 1000, if over 1000 then use default 0.
def MYALGO(reflist,frame_size):
    frame,db_list= CreateFrame_RandomDirty(reflist,frame_size)
    pf=frame_size
    it=0
    dw=0
    for i in range(100000):
        #check if page fault happens
        if IfPageFault(i,reflist,frame,frame_size):
            it+=1
            pf+=1
            #choose victim page from the page frame, use MYALGO concept!
            #record future might loc in frame, create l to store them.
            l=[]
            for j in range(frame_size):
                for k in range(i,1000):
                    loc=100000
                    if frame[j] == reflist[k]:
                        loc = j
                        break
                l.append(loc)
            #find the farest loc in l, the index of it is which we want to replace.
            FAR=0
            FAR_index=0
            for j in range(frame_size):
                if l[j] > FAR:
                    FAR = l[j]
                    FAR_index=j    
            #replace it
            frame[FAR_index] = reflist[i]
            #See if dirty bit=1 when page fault happens, if it is, then disk write.
            if db_list[FAR_index] == 1:
                dw+=1
                db_list[FAR_index] = 0
            else:
                db_list[FAR_index] = 1
    
    return pf,it,dw

def HW1(algo_mode, reflist_mode, frame_size):
    reflist = CreateStr(reflist_mode)
    if algo_mode == 'FIFO':
        pf, it, dw = FIFO(reflist,frame_size)
    elif algo_mode == 'OPT':
        pf, it, dw = OPT(reflist,frame_size)
    elif algo_mode == 'ESC':
        pf, it, dw = ESC(reflist,frame_size)
    elif algo_mode == 'MYALGO':
        pf, it, dw = MYALGO(reflist,frame_size)
    return pf, it, dw

def CompareAlgo(input_ref):
    fifo_ref_pf=[]; fifo_ref_it=[]; fifo_ref_dw=[]
    opt_ref_pf=[]; opt_ref_it=[]; opt_ref_dw=[]
    esc_ref_pf=[]; esc_ref_it=[]; esc_ref_dw=[]
    myalgo_ref_pf=[]; myalgo_ref_it=[]; myalgo_ref_dw=[]
    
    for i in range(10):
        frame_size = i*10+10
        print('========FIFO,',input_ref,'========')
        pf, it, dw = HW1('FIFO',input_ref,frame_size)
        fifo_ref_pf.append(pf);fifo_ref_it.append(it);fifo_ref_dw.append(dw)
        print('========OPT,',input_ref,'========')
        pf, it, dw = HW1('OPT',input_ref,frame_size)
        opt_ref_pf.append(pf);opt_ref_it.append(it);opt_ref_dw.append(dw)
        print('========ESC,',input_ref,'========')
        pf, it, dw = HW1('ESC',input_ref,frame_size)
        esc_ref_pf.append(pf);esc_ref_it.append(it);esc_ref_dw.append(dw)
        print('========MYALGO,',input_ref,'========')
        pf, it, dw = HW1('MYALGO',input_ref,frame_size)
        myalgo_ref_pf.append(pf);myalgo_ref_it.append(it);myalgo_ref_dw.append(dw)
        
    #plot mode(pf, it, dw),input_aglo in FIFO, OPT, ESC, MINE
    #'pf':
    plt.plot(fifo_ref_pf)
    plt.plot(opt_ref_pf)
    plt.plot(esc_ref_pf)
    plt.plot(myalgo_ref_pf)
    plt.title('Page Fault('+input_ref+')')
    plt.ylabel('Page Fault')
    plt.xlabel('Frame Size*10+10')
    plt.legend(['FIFO','OPT','ESC','MYALGO'], loc='upper left')
    plt.show()
    #'it':
    plt.plot(fifo_ref_it)
    plt.plot(opt_ref_it)
    plt.plot(esc_ref_it)
    plt.plot(myalgo_ref_it)
    plt.title('Interrupt('+input_ref+')')
    plt.ylabel('Interrupt')
    plt.xlabel('Frame Size*10+10')
    plt.legend(['FIFO','OPT','ESC','MYALGO'], loc='upper left')
    plt.show()
    #'dw':
    plt.plot(fifo_ref_dw)
    plt.plot(opt_ref_dw)
    plt.plot(esc_ref_dw)
    plt.plot(myalgo_ref_dw)
    plt.title('Disk Write('+input_ref+')')
    plt.ylabel('Disk Write')
    plt.xlabel('Frame Size*10+10')
    plt.legend(['FIFO','OPT','ESC','MYALGO'], loc='upper left')
    plt.show()

#Notice that if there is any error: must be typing error like 'RANDOM' -> 'Random'.
if __name__ == '__main__':
    input_ref = input('plz input a kind of reference string like RANDOM,LOCALITY,MYSTR:', )
    CompareAlgo(input_ref)