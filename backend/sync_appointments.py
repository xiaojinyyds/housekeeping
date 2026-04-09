from app.core.database import SessionLocal, engine
from sqlalchemy import text, inspect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sync_schema():
    inspector = inspect(engine)
    columns = inspector.get_columns('appointments')
    existing_columns = {col['name'] for col in columns}
    
    # Model fields definitions (manual mapping to ensure correctness)
    # Based on app/models/appointment.py
    required_columns = {
        'reject_reason': "TEXT COMMENT '拒绝原因'",
        'cancelled_by': "VARCHAR(10) COMMENT '取消方：user/worker'",
        # Check others that might be missing
        # 'contact_name': "VARCHAR(50) COMMENT '联系人'", 
        # 'contact_phone': "VARCHAR(20) COMMENT '联系电话'",
        # 'remark': "TEXT COMMENT '用户备注'",
        # 'cancel_reason': "TEXT COMMENT '取消原因'",
        # 'started_at': "TIMESTAMP",
        # 'completed_at': "TIMESTAMP",
        # 'accepted_at': "TIMESTAMP",
        # 'cancelled_at': "TIMESTAMP",
    }
    
    # Check what is already there (renamed ones should be there from previous step)
    # Step 563 script renamed:
    # phone -> contact_phone
    # note -> remark
    # cancellation_reason -> cancel_reason
    
    # Let's add specifically what caused the error + anything else suspicious
    
    db = SessionLocal()
    
    try:
        if 'reject_reason' not in existing_columns:
            logger.info("Adding reject_reason...")
            db.execute(text(f"ALTER TABLE appointments ADD COLUMN reject_reason {required_columns['reject_reason']}"))
            
        if 'cancelled_by' not in existing_columns:
            logger.info("Adding cancelled_by...")
            db.execute(text(f"ALTER TABLE appointments ADD COLUMN cancelled_by {required_columns['cancelled_by']}"))
            
        # Re-verify critical ones from previous steps just in case
        if 'contact_name' not in existing_columns:
             # It was in the original 'DESCRIBE' list in Step 559 but let's be safe
             logger.info("Adding contact_name...")
             db.execute(text("ALTER TABLE appointments ADD COLUMN contact_name VARCHAR(50) COMMENT '联系人'"))

        db.commit()
        logger.info("Schema sync completed.")
        
    except Exception as e:
        logger.error(f"Error syncing schema: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    sync_schema()
