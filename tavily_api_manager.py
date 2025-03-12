import pymysql
import os
from datetime import datetime
from typing import Optional
import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TavilyApiManager:
    """
    从数据库管理Tavily API密钥的类。
    - 获取time列值最小的API密钥
    - 每次使用后增加time计数
    - 每月1日重置所有time值为0
    """
    
    def __init__(self, host="localhost", user="root", password="", database="data"):
        """
        初始化Tavily API管理器
        
        Args:
            host: 数据库主机
            user: 数据库用户名
            password: 数据库密码
            database: 数据库名称
        """
        self.host = "192.168.7.125"
        self.user = "allenqiangwei"
        self.password = "allen1982qiang"
        self.database = "data"
        self._create_table_if_not_exists()
        self._reset_time_if_first_day_of_month()
        
    def _get_connection(self) -> pymysql.connections.Connection:
        """获取数据库连接"""
        return pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            cursorclass=pymysql.cursors.DictCursor
        )
    
    def _create_table_if_not_exists(self) -> None:
        """如果表不存在，创建tavily表"""
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tavily (
                        code VARCHAR(255) PRIMARY KEY,
                        time INT DEFAULT 0,
                        last_reset VARCHAR(10)
                    )
                """)
            conn.commit()
        except Exception as e:
            logger.error(f"创建表时出错: {e}")
        finally:
            conn.close()
    
    def _reset_time_if_first_day_of_month(self) -> None:
        """如果是每月的第一天，将所有time值重置为0"""
        today = datetime.now()
        if today.day == 1:  # 每月第一天
            try:
                conn = self._get_connection()
                with conn.cursor() as cursor:
                    # 检查上次重置日期
                    cursor.execute("SELECT last_reset FROM tavily LIMIT 1")
                    result = cursor.fetchone()
                    
                    if result:
                        last_reset = result['last_reset']
                        last_reset_date = datetime.strptime(last_reset, "%Y-%m-%d") if last_reset else None
                        
                        # 如果上次重置不是本月，则进行重置
                        if not last_reset_date or last_reset_date.month != today.month or last_reset_date.year != today.year:
                            self._reset_all_time_values(conn, cursor, today)
                    else:
                        # 没有记录，但表已存在
                        self._reset_all_time_values(conn, cursor, today)
                        
            except Exception as e:
                logger.error(f"重置time值时出错: {e}")
            finally:
                conn.close()
    
    def _reset_all_time_values(self, conn: pymysql.connections.Connection, cursor, today: datetime) -> None:
        """重置所有time值为0并更新last_reset日期"""
        today_str = today.strftime("%Y-%m-%d")
        cursor.execute("UPDATE tavily SET time = 0, last_reset = %s", (today_str,))
        conn.commit()
        logger.info(f"已将所有tavily记录的time值重置为0，日期: {today_str}")
    
    def get_api_key(self) -> Optional[str]:
        """
        获取time值最小的API密钥并增加其time值
        
        Returns:
            str: API密钥，如果没有可用的密钥则返回None
        """
        try:
            conn = self._get_connection()
            with conn.cursor() as cursor:
                # 获取time值最小的记录
                cursor.execute("SELECT code FROM tavily ORDER BY time ASC LIMIT 1")
                result = cursor.fetchone()
                
                if not result:
                    logger.warning("tavily表中没有可用的API密钥")
                    return None
                
                api_key = result['code']
                
                # 增加time值
                cursor.execute("UPDATE tavily SET time = time + 1 WHERE code = %s", (api_key,))
                conn.commit()
                
                logger.info(f"已获取API密钥，使用计数已增加")
                return api_key
                
        except Exception as e:
            logger.error(f"获取API密钥时出错: {e}")
            return None
        finally:
            conn.close()

# 创建单例实例
_tavily_api_manager = None

def get_tavily_api_key() -> Optional[str]:
    """
    获取Tavily API密钥的便捷函数
    
    Returns:
        str: 从数据库获取的API密钥，或者环境变量中的密钥作为备用
    """
    global _tavily_api_manager
    
    # 首先尝试从环境变量获取API密钥（作为备用）
    env_api_key = os.environ.get("TAVILY_API_KEY")
    
    # 然后尝试从数据库获取API密钥
    if _tavily_api_manager is None:
        try:
            # 可以从环境变量获取数据库连接信息
            host = os.environ.get("DB_HOST", "localhost")
            user = os.environ.get("DB_USER", "root")
            password = os.environ.get("DB_PASSWORD", "")
            database = os.environ.get("DB_NAME", "data")
            
            _tavily_api_manager = TavilyApiManager(
                host=host, 
                user=user, 
                password=password, 
                database=database
            )
        except Exception as e:
            logger.error(f"初始化TavilyApiManager时出错: {e}")
            return env_api_key
    
    db_api_key = _tavily_api_manager.get_api_key()
    
    # 返回数据库中的密钥，如果没有则返回环境变量中的密钥
    return db_api_key if db_api_key else env_api_key 