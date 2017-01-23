
LIB_DIR=lib

ifeq ($(WINDIR),)
	S=:
else
	S=\;
endif

.PHONY: test


update: compiler rts sysj

sysj:
	(cd test; java -cp '.$(S)../lib/*' JavaPrettyPrinter a.sysj)

compiler:
	(cd systemj; ant jar)
	cp systemj/jdom.jar $(LIB_DIR)
	mv systemj/SystemJCompiler* $(LIB_DIR)

rts:
	cp -rf lib/gson*.jar systemjrte/lib
	cp -rf updates/systemjrte .
	(cd systemjrte; ant desktop)
	mv systemjrte/SystemJRuntime* $(LIB_DIR)

run:
	(cd test; java -cp '.$(S)../lib/*' systemj.bootstrap.SystemJRunner a.xml)

clean:
	(cd systemj; ant clean)
	(cd systemjrte; ant clean)
	rm -rf lib/SystemJ*.jar lib/jdom.jar
