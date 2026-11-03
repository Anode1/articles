/* bench_wake: time iac's send->recv wake around the real binary.
 * usage: bench_wake <iac> <room> <base_size> <mode> <n>
 *   mode wake    : reader parked at the end of a base_size log; one send; time until recv returns
 *   mode catchup : reader cursor at 0, message already appended; time until recv returns
 * prints CSV: mode,base_size,iter,send_ms,wake_ms
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <sys/stat.h>

static double now(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec*1e3 + t.tv_nsec/1e6; }
static pid_t spawn(char *const argv[]){ pid_t p=fork(); if(p==0){ int d=open("/dev/null",O_RDWR); dup2(d,0); dup2(d,1); dup2(d,2); execv(argv[0],argv); _exit(127);} return p; }
static void set_cursor(const char *room, long c){ char p[4096]; snprintf(p,sizeof p,"%s/bob.cur",room); FILE *f=fopen(p,"w"); fprintf(f,"%ld\n",c); fclose(f); }
static void reset_log(const char *room, long size){ char p[4096]; snprintf(p,sizeof p,"%s/log",room); truncate(p,size); }

int main(int argc, char **argv){
    if(argc<6){ fprintf(stderr,"usage\n"); return 2; }
    char *iac=argv[1], *room=argv[2]; long base=atol(argv[3]); char *mode=argv[4]; int n=atoi(argv[5]);
    char *recv_argv[]={iac,"recv",room,"bob","10",NULL};
    char *send_argv[]={iac,"send",room,"bob","ping",NULL};
    setenv("IAC_FROM","alice",1);
    for(int i=0;i<n;i++){
        reset_log(room,base);
        int st;
        if(strcmp(mode,"wake")==0){
            set_cursor(room,base);
            pid_t r=spawn(recv_argv);
            usleep(100000);                      /* let recv park on inotify */
            double t0=now();
            pid_t s=spawn(send_argv); waitpid(s,&st,0);
            double t1=now();
            waitpid(r,&st,0);
            double t2=now();
            printf("wake,%ld,%d,%.3f,%.3f\n",base,i,t1-t0,t2-t0);
        } else {
            set_cursor(room,0);
            pid_t s=spawn(send_argv); waitpid(s,&st,0);
            double t0=now();
            pid_t r=spawn(recv_argv); waitpid(r,&st,0);
            double t2=now();
            printf("catchup,%ld,%d,0,%.3f\n",base,i,t2-t0);
        }
        fflush(stdout);
    }
    return 0;
}
