@echo off
setlocal EnableDelayedExpansion

echo ----- jumplist
jlecmd -q -d MRU\Files\jmp --mp --csv MRU\Files >> process_log.txt

echo ----- lnk
lecmd -q -d MRU\Files\lnk --mp --csv MRU\Files >> process_log.txt

echo ----- prefetch
pecmd -q -d MRU\Prog\prefetch --mp --csv MRU\Prog >> process_log.txt

echo ----- recentfilecache
for /R ".\MRU\Prog\recentfilecache\" %%f in (RecentFileCache.bcf) do (
	recentfilecacheparser -q -f  %%f --mp --csv MRU\Prog >> process_log.txt
)

echo ----- amcache
for /R ".\MRU\Prog\amcache\" %%f in (Amcache.hve) do (
    registryFlush -f %%f --overwrite >> process_log.txt
    amcacheparser -f %%f -i --mp --csv MRU\Prog >> process_log.txt"
)

echo ----- sccm
for /R ".\MRU\Prog\sccm\" %%f in (OBJECTS.DATA) do (
	for %%a in (%%f) do for %%b in ("%%~dpa\.") do set "parent=%%~nxb"
	python D:\git\WMI_Forensics\CCM_RUA_Finder.py -i %%f -o MRU\Prog\sccm_!parent!.tsv >> process_log.txt
)

echo ----- appcompatcache
for /R ".\MRU\Registry\" %%f in (SYSTEM) do (
    registryFlush -f %%f --overwrite
    appcompatcacheparser -f Registry\SYSTEM --csv MRU\Prog >> process_log.txt
)

echo ----- timeline
for /R ".\MRU\Timeline\" %%f in (ActivitiesCache.db) do (
	wxtcmd -f %%f --csv MRU\Timeline >> process_log.txt
)

echo ----- srum
for /R ".\MRU\Prog\srum\" %%f in (SRUDB.dat) do (
	for %%a in (%%f) do for %%b in ("%%~dpa\.") do set "parent=%%~nxb"
	D:\git\srum-dump\srum_dump.exe -i MRU\Prog\srum\SRUDB.dat -o MRU\Prog\srum_!parent!.xlsx -t D:\git\srum-dump\SRUM_TEMPLATE.xlsx -r Registry\SOFTWARE >> process_log.txt
)

echo ----- registryFlush
echo SAM
registryFlush -f Registry\SAM --overwrite >> process_log.txt
echo SECURITY
registryFlush -f Registry\SECURITY --overwrite >> process_log.txt
echo SOFTWARE
registryFlush -f Registry\SOFTWARE --overwrite >> process_log.txt
echo Syscache
registryFlush -f MRU\Prog\syscache\Syscache.hve --overwrite >> process_log.txt

echo ----- syscache
syscache -f MRU\Prog\syscache\Syscache.hve -o MRU\Prog >> process_log.txt

echo ----- registry
autoripy --rr D:\git\RegRipper2.8\ -s Registry -a MRU\Prog\amcache -m Registry -r Registry >> process_log.txt

echo ----- evtx
evtx2json -d OSLogs -o OSLogs\ --dedup >> process_log.txt
