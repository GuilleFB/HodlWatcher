FROM minio/minio:latest

ENV MINIO_ROOT_USER=tu_usuario_admin
ENV MINIO_ROOT_PASSWORD=tu_contraseña_segura

EXPOSE 9000
EXPOSE 9001

CMD ["server", "/data", "--console-address", ":9001"]
