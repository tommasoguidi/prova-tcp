import time
import base64
from unaiverse.networking.p2p import P2P
from unaiverse.networking.p2p.messages import Msg


def run_echo():
    P2P.setup_library(enable_logging=True)
    print("--- Avvio Echo Node ---")
    node_config = {
            "identity_dir": "./id_echo",
            "port": 20200,
            "ips": None,
            "enable_relay_client": False,
            "enable_relay_service": False,
            "knows_is_public": False,
            "max_connections": 1000,
            "enable_tls": False,
            "domain_name": None,
            "tls_cert_path": None,
            "tls_key_path": None,
            "dht_enabled": True,
            "dht_mode": 'client',
            "dht_keep": True
        }
    node = P2P(**node_config)
    
    print(f"\nMY ID: {node.peer_id}")
    print("MY ADDRS:")
    for addr in node.addresses:
        print(f"  {addr}")
    print("\nIn ascolto...\n")

    try:
        while True:
            # 1. Preleviamo i messaggi raw (lista di bytes)
            raw_msgs = node.pop_messages()
            
            for raw_m in raw_msgs:
                try:
                    base64_data = raw_m.get("data")
                    decoded_data = base64.b64decode(base64_data)
                    msg_obj = Msg.from_bytes(decoded_data)
                    
                    sender = msg_obj.sender
                    content = msg_obj.content # Decodifica automatica JSON/Stringa
                    
                    print(f"Ricevuto da {sender[:5]}...: {content}")

                    # 3. Costruiamo la risposta
                    # Formato channel richiesto da P2P.py: MIO_ID::dm:TARGET_ID
                    reply_channel = f"{node.peer_id}::dm:{sender}"
                    
                    reply_msg = Msg(
                        sender=node.peer_id,
                        content=f"ECHO: {content}",
                        channel=reply_channel,
                        content_type=Msg.MISC
                    )
                    
                    # 4. Inviamo i bytes serializzati
                    node.send_message_to_peer(reply_channel, reply_msg.to_bytes())
                    print(f" -> Risposto a {sender[:5]}...")
                    
                except Exception as e:
                    print(f"Errore processamento msg: {e}")

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Chiusura...")
        node.close()

if __name__ == "__main__":
    run_echo()
