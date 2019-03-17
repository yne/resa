FROM ubuntu
RUN apt update && apt install -y python3-flask python3-jwt python3-ldap ssmtp mailutils
COPY . /root/
WORKDIR /root
EXPOSE 5000 25 465 587
CMD ["./app.py"]
